# 데이터 웨어하우스를 이용한 대시보드 구성
## 주제: 영화 트렌드 대시보드
## Programmers 데브코스 Data Engineering 5기 
- <b>Team</b>`1잘하조`
  - <b>김동환</b>
  - <b>윤대열</b>
  - <b>이상원</b>
  - <b>설연수</b>
  - <b>김유빈</b>
- **프로젝트 진행 기간**: 2025.01.06 ~ 2025.01.09

## 목차
###### 1. 프로젝트 개요
###### 2. 활용 기술
###### 3. 프로젝트 세부내용
###### 4. 프로젝트 결과

## 1. 프로젝트 개요
### 프로젝트 주제 선정
영화 산업은 문화와 경제에 큰 영향을 미치는 분야로, 끊임없이 변화하는 관객의 선호도와 트렌드를 분석하는 것이 중요합니다.
  
최근 OTT 플랫폼의 확산, 특정 장르의 인기도 변화 등 영화 시장의 복잡성이 증가하며,
  
데이터 기반 의사 결정의 필요성이 커지고 있기에 이번 주제를 기획하게 되었습니다.
  
### 프로젝트 주요 목표
- AWS S3, Redshift, Superset(Preset) 등 최신 클라우드 및 데이터 시각화 기술을 활용
- 대용량 데이터의 분석
- 직관적이고 유용한 대시보드 시스템 구축

### 기술적 목표
- 웹크롤링, OPEN API를 이용하여 데이터 수집
- AWS S3에 데이터 적재 및 전처리
- Redshift에 COPY하여 사용 및 이해
- Superset(Preset)을 사용하여 Chart 작성 및 Dashboard 제작하여 데이터 시각화

## 2. 활용 기술 
### 데이터 소스
> [KOFIC 영화관 입장권 통합전산망 :: 일별 박스오피스](https://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do)

> [KOBIS OPEN API 서비스](https://www.kobis.or.kr/kobisopenapi/homepg/main/main.do)

### 데이터 수집
`Python` `Selenium` `Requests`

### 데이터 처리
`pywin32` `Pandas`

### 데이터 적재
`AWS S3` `AWS Redshift` `boto3` `Python Schedule`

### 데이터 시각화
`Preset`

### 협업 Tools
`Github` `Slack` `Zep` `Notion`

## 3. 프로젝트 세부내용
<img src="https://github.com/user-attachments/assets/5cfce004-4e93-4bad-8c88-10c8dc5a8bf5"  width="1000" height="500"/><br>

### 영화 별 매출액, 전날 관객 수

### 장르 별(+기간) 관객 수

### 상영관 별 관객 수

### 기간(연간,월간,주간) 별 관객 수

### 배우별 인지도

## 4. 프로젝트 결과
추후 대시보드 사진 삽입

### 기대효과

### 개선점
