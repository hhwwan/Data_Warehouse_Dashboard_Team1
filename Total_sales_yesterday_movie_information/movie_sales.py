import boto3
import psycopg2
import const
import os

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
    local_file_path = "./Total_sales_yesterday_movie_information/data/movie_total_sales.csv"  # 저장 경로

    # S3 설정
    bucket_name = const.BUCKET_NAME
    s3_file_name = const.S3_FILE_NAME
    s3_path = f"s3://{bucket_name}/{s3_file_name}"

    # Redshift 설정
    redshift_dsn = const.REDSHIFT_DSN
    account_id = const.ACCOUNT_ID
    role = const.ROLE
    table_name = const.TABLE_NAME

    try:
        # S3 업로드
        print("S3에 데이터 업로드 중...")
        upload_to_s3(local_file_path, bucket_name, s3_file_name)

        # Redshift 적재
        print("Redshift에 데이터 적재 중...")
        copy_to_redshift(redshift_dsn, s3_path, table_name, account_id, role)

        print("파이프라인 실행 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
