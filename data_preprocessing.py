import pandas as pd

# 데이터 파일 로드
df = pd.read_csv('combined.csv', encoding="utf-8-sig")

# 'voting_date'를 datetime 형식으로 변환
df['voting_date'] = pd.to_datetime(df['voting_date'], errors='coerce')

# title별로 가장 최신의 voting_date를 찾고, 해당 날짜에서 total_audience가 100 미만인 데이터를 삭제
def filter_by_latest_voting_date(group):
    latest_voting_date = group['voting_date'].max()  # 가장 최신 voting_date 찾기
    group = group[(group['voting_date'] != latest_voting_date) | (group['total_audience'] >= 1000)]  # 조건에 맞는 데이터만 남기기
    return group

# title별로 그룹화하여 함수 적용
df = df.groupby('title', group_keys=False).apply(filter_by_latest_voting_date)

# released_date 값이 없을 때는 2000-01-01로 변경
df['released_date'].fillna('1900-01-01', inplace=True)
df = df.dropna()
# performers에 들어있는 performer가 10개가 넘어간다면 최초 10개 데이터만 남기기
df['performers'] = df['performers'].apply(lambda x: ','.join(x.split(',')[:10]))

df = df.fillna({
    'sales': 0,
    'total_sales': 0,
    'audience_num': 0, 
    'total_audience': 0,
    'genre': 'Unknown',
    'performers': 'Unknown'})

# 전처리된 데이터 확인
print(df.head())

# 전처리된 데이터 저장
df.to_csv('main_data.csv', index=False, encoding="utf-8-sig")
