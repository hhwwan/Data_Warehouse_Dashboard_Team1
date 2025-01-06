import pandas as pd

# CSV 파일 불러오기
df = pd.read_csv('./raw_data/processing_1/processing_2/movie_total_sales.csv', encoding='utf-8')

# 헤더 변경
df.columns = ['rank_num', 'title', 'director', 'production_comp_name', 'importer_name', 
            'distributor_name', 'released_date', 'movie_type', 'movie_format', 'country', 
            'screen_num', 'total_sales', 'audience_num', 'seoul_total_sales', 'seoul_audience_num', 
            'genre', 'film_ratings', 'category']

# 'rank_num' 열을 1부터 순차적으로 변경
df['rank_num'] = range(1, len(df) + 1)

# 모든 열에서 쉼표 제거
df = df.applymap(lambda x: str(x).replace(',', '') if isinstance(x, str) else x)

# 처리된 데이터 저장
df.to_csv('./raw_data/processing_1/processing_2/movie_total_sales.csv', index=False, encoding='utf-8-sig')

print("success!")
