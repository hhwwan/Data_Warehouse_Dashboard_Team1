import time
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ChromeDriver 설정
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=options)

# 웹사이트 열기
url = 'https://www.kobis.or.kr/kobis/business/stat/boxs/findDailyMultichainList.do'
driver.get(url)

# 시작 날짜와 종료 날짜 설정
start_date = datetime(2019, 1, 1)
end_date = datetime(2024, 12, 31)
delta = timedelta(days=7)  # 7일 단위

# 데이터 저장 리스트
data = []

while start_date <= end_date:
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = (start_date + delta - timedelta(days=1)).strftime('%Y-%m-%d')

    try:
        # "달력" 버튼 클릭
        calendar_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="searchForm"]/div/div[1]/div/div[1]/label'))
        )
        calendar_button.click()

        # 연도 변경
        year_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'ui-datepicker-year'))
        )
        year_dropdown.click()
        target_year = str(start_date.year)
        driver.find_element(By.XPATH, f"//option[@value='{target_year}']").click()

        # 월 변경
        month_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'ui-datepicker-month'))
        )
        month_dropdown.click()
        target_month = str(start_date.month - 1)  # Selenium의 월은 0부터 시작
        driver.find_element(By.XPATH, f"//option[@value='{target_month}']").click()

        # 날짜 선택
        target_day = str(start_date.day)
        day_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[text()='{target_day}']"))
        )
        day_button.click()

        # 조회 버튼 클릭
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn_blue') and text()='조회']"))
        )
        driver.execute_script("arguments[0].click();", search_button)

        # 데이터 로드 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'tbl_comm'))
        )
        time.sleep(5)

        # 페이지 소스 가져오기
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 날짜 확인
        date_title = soup.find('div', class_='board_tit').find('h4').get_text(strip=True)

        # 테이블 데이터 추출
        rows = soup.select("table.tbl_comm tbody tr")
        current_movie, current_chain = None, None

        for row in rows:
            cols = row.find_all("td")

            # 영화명
            movie_cell = row.select_one("td.tal a")
            if movie_cell:
                current_movie = movie_cell.get_text(strip=True)

            # 체인명
            chain_cell = row.select_one("td.tac[rowspan]")
            if chain_cell:
                current_chain = chain_cell.get_text(strip=True)

            # "계" 행 데이터
            if len(cols) > 0 and cols[0].get_text(strip=True) == "계":
                screenings = cols[1].get_text(strip=True).replace(",", "")  # 상영 횟수
                screen_share = cols[3].get_text(strip=True)  # 상영 점유율
                data.append([date_title, current_movie, current_chain, screenings, screen_share])

    except Exception as e:
        print(f"오류 발생 (날짜: {start_date_str}): {e}")

    # 다음 주로 이동
    start_date += delta

# 브라우저 종료
driver.quit()

# 데이터프레임으로 변환
df = pd.DataFrame(data, columns=['조회일', '영화명', '체인명', '상영횟수', '상영점유율(%)'])

# 날짜 수정 로직
updated_dates = []
current_date = None
row_counter = 0

for idx, row in df.iterrows():
    if row_counter % 140 == 0:
        current_date = datetime.strptime(row['조회일'].split('(')[0], '%Y년 %m월 %d일')
        sub_date = current_date
    if row_counter % 20 == 0 and row_counter % 140 != 0:
        sub_date -= timedelta(days=1)
    updated_dates.append(sub_date.strftime('%Y년 %m월 %d일(%a)'))
    row_counter += 1

df['조회일'] = updated_dates

# 날짜 데이터 변환 및 정렬
df['조회일'] = pd.to_datetime(df['조회일'], format='%Y년 %m월 %d일(%a)')
chunk_size = 20
chunks = [df.iloc[i:i+chunk_size] for i in range(0, len(df), chunk_size)]
sorted_chunks = sorted(chunks, key=lambda x: x['조회일'].iloc[0])
sorted_df = pd.concat(sorted_chunks).reset_index(drop=True)
sorted_df['조회일'] = sorted_df['조회일'].dt.strftime('%Y년 %m월 %d일(%a)')

# 날짜 형식 변경 및 추가 데이터 처리
sorted_df['Date'] = pd.to_datetime(sorted_df['조회일'].str.extract(r'(\d{4}년 \d{2}월 \d{2}일)')[0], format='%Y년 %m월 %d일')
sorted_df['day_of_week'] = sorted_df['Date'].dt.day_name()
sorted_df["Screen_Share"] = sorted_df["상영점유율(%)"].str.rstrip("%").astype(float)
sorted_df = sorted_df.drop(columns=["상영점유율(%)"])

# 정렬된 데이터 저장
output_path = ''
sorted_df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"날짜 오름차순으로 정렬된 파일이 저장되었습니다: {output_path}")
