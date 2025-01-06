import pandas as pd
import os

# 병합할 엑셀 파일들이 있는 폴더 경로
folder_path = 'C:/Users/hwan/Desktop/git_hub/Data_Warehouse_Dashboard_Team1/raw_data/processing_1'

# 폴더 내 모든 엑셀 파일을 찾기
excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

# 엑셀 파일을 읽어서 하나의 DataFrame으로 병합
merged_df = pd.DataFrame()

for file in excel_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_excel(file_path)
    
    # 파일에서 불필요한 빈 행 제거 (NaN이 포함된 행 제거)
    df.dropna(how='all', inplace=True)
    
    merged_df = pd.concat([merged_df, df], ignore_index=True)

# 병합된 데이터에서 숫자 열을 int로 변환
numeric_columns = ['순번', '전국 스크린수', '전국 매출액', '전국 관객수', '서울 매출액', '서울 관객수']  # 숫자 열 목록

for col in numeric_columns:
    merged_df[col] = merged_df[col].astype('Int64')  # Int64로 변환 (NaN 처리 가능)

# '개봉일' 열을 날짜 형식으로 변환 (YYYY-MM-DD HH:MM:SS 형식)
merged_df['개봉일'] = pd.to_datetime(merged_df['개봉일']).dt.strftime('%Y-%m-%d %H:%M:%S')

# 병합된 데이터를 CSV 파일로 저장 (UTF-8 인코딩)
merged_df.to_csv('./raw_data/processing_1/processing_2/movie_total_sales.csv', index=False, encoding='utf-8-sig')

print("success!")
