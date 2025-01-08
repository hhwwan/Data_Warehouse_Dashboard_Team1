import schedule
import time
import requests
import csv
import boto3
import psycopg2
import os
from datetime import datetime, timedelta

def fetch_box_office_data(api_key, target_date, local_file_path):
    """
    API에서 일별 박스오피스 데이터를 가져와 CSV 파일로 저장
    """
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        daily_box_office_list = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        with open(local_file_path, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = daily_box_office_list[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in daily_box_office_list:
                writer.writerow(entry)
        print("CSV 파일로 저장되었습니다.")
    else:
        raise Exception(f"API 호출 실패: {response.status_code}")

def update_csv_headers(file_path):
    """
    기존 CSV 파일의 헤더를 새로운 헤더로 변경
    """
    original_headers = [
        'rnum', 'rank', 'rankInten', 'rankOldAndNew', 'movieCd', 'movieNm', 'openDt', 
        'salesAmt', 'salesShare', 'salesInten', 'salesChange', 'salesAcc', 'audiCnt', 
        'audiInten', 'audiChange', 'audiAcc', 'scrnCnt', 'showCnt'
    ]

    new_headers = [
        'rank_num', 'ranking', 'day_increase_decrease', 'new_entry', 'code', 'title', 
        'released_date', 'day_sales', 'day_sales_ratio', 'day_sales_increase_decrease', 
        'day_sales_increase_decrease_ratio', 'total_sales', 'day_audience_num', 
        'day_audience_increase_decrease', 'day_audience_increase_decrease_ratio', 
        'total_audience_num', 'day_screen_num', 'day_screen_show'
    ]

    # CSV 파일의 헤더를 변경
    with open(file_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    # 기존 내용 유지하며 첫 줄의 헤더 변경
    lines[0] = ','.join(new_headers) + '\n'

    with open(file_path, 'w', encoding='utf-8') as outfile:
        outfile.writelines(lines)

    print("CSV 헤더 변경 완료.")

def add_voting_date(file_path):
    """
    CSV 파일에 voting_date 열 추가 및 어제 날짜로 채우기
    """
    # 어제 날짜를 YYYY-MM-DD 형식으로 가져오기
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # CSV 파일 읽고 수정하기
    with open(file_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    # 첫 번째 줄(헤더)을 읽고 voting_date 추가
    header = rows[0]
    new_header = ['voting_date'] + header
    rows[0] = new_header

    # 나머지 줄에 어제 날짜 추가
    for i in range(1, len(rows)):
        rows[i] = [yesterday] + rows[i]

    # 수정된 내용을 원본 파일에 덮어쓰기
    with open(file_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)

    print(f"파일이 '{file_path}'에 voting_date 추가 완료되었습니다.")

def upload_to_s3(local_file_path, bucket_name, s3_file_name):
    """
    CSV 파일을 S3 버킷에 업로드
    """
    s3_client = boto3.client('s3')
    if os.path.exists(local_file_path):
        s3_client.upload_file(local_file_path, bucket_name, s3_file_name)
        print(f"파일이 S3에 업로드되었습니다: {bucket_name}/{s3_file_name}")
    else:
        raise FileNotFoundError(f"파일이 존재하지 않습니다: {local_file_path}")

def copy_to_redshift(redshift_dsn, s3_path, table_name, account_id, role):
    """
    S3에 저장된 CSV 파일을 Redshift 테이블로 적재
    기존 데이터를 삭제하고 새 데이터를 적재
    """
    conn = psycopg2.connect(redshift_dsn)
    cur = conn.cursor()

    try:
        # 기존 데이터 삭제
        truncate_query = f"TRUNCATE TABLE {table_name};"
        cur.execute(truncate_query)
        print(f"테이블 데이터 초기화 완료: {table_name}")

        # 새 데이터 적재
        copy_query = f"""
            COPY {table_name}
            FROM '{s3_path}'
            credentials 'aws_iam_role=arn:aws:iam::{account_id}:role/{role}'
            delimiter ',' dateformat 'auto' timeformat 'auto' IGNOREHEADER 1 removequotes;
        """
        cur.execute(copy_query)
        conn.commit()
        print("Redshift 데이터 적재 완료")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def main():
    """
    전체 파이프라인 실행
    """
    # 설정 정보
    api_key = "59d9ade99e237278bcb364de7ae8c0a7"  # API 키
    # 조회날짜
    yesterday = datetime.now() - timedelta(days=1)
    target_date = yesterday.strftime("%Y%m%d")  # 조회 날짜 (YYYYMMDD 포맷)
    local_file_path = "./Total_sales_yesterday_movie_information/data/daily_box_office.csv"  # 저장 경로

    # S3 설정
    bucket_name = "2nd-team1-bucket"
    s3_file_name = "hwan/daily_box_office.csv"
    s3_path = f"s3://{bucket_name}/{s3_file_name}"

    # Redshift 설정
    redshift_dsn = (
        "postgresql://admin:2ndTeam1!@team1-workgroup.490004631923.us-west-2.redshift-serverless.amazonaws.com:5439/dev"
    )
    account_id = "490004631923"
    role = "redshift.read.s3"
    table_name = "raw_data.yesterday_audience"

    try:
        # 데이터 수집
        print("API에서 데이터 수집 중...")
        fetch_box_office_data(api_key, target_date, local_file_path)

        # 헤더 변경
        print("CSV 파일 헤더 변경 중...")
        update_csv_headers(local_file_path)

        # voting_date 추가
        print("CSV 파일에 voting_date 추가 중...")
        add_voting_date(local_file_path)

        # S3 업로드
        print("S3에 데이터 업로드 중...")
        upload_to_s3(local_file_path, bucket_name, s3_file_name)

        # Redshift 적재
        print("Redshift에 데이터 적재 중...")
        copy_to_redshift(redshift_dsn, s3_path, table_name, account_id, role)

        print("파이프라인 실행 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")

# 스케줄링 설정
schedule.every().day.at("09:00").do(main)

print("스케줄러가 실행 중입니다. 프로그램을 종료하지 마세요.")

while True:
    schedule.run_pending()
    time.sleep(1)

# if __name__ == "__main__":
#     main()