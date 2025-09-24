
import requests
import pandas as pd
import pymysql
import os
from dotenv import load_dotenv


load_dotenv()

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

conn = pymysql.connect(
    host=host,
    user=user,
    password=password,
    charset="utf8mb4"
)

cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS 6team;")
cursor.execute("USE 6team;")

API_URL = "https://api.odcloud.kr/api/15039545/v1/uddi:f8f879ad-68cf-40fb-8ccc-cb36eaf1baca"
SERVICE_KEY = "8ae9566a50f6b632198d0863de24d4fdb8a0491b5ad384b8d83a7302a3c00ba9"

res = requests.get(API_URL, params= {
    "serviceKey": SERVICE_KEY,
    "page": 1,
    "perPage": 1000,
    "returnType" : "JSON"})
data = res.json()["data"]
df = pd.DataFrame(data)

# 지역명 변환 함수
def convert_region_name(address):
    first_word = address.split()[0]
    
    # 시/도 이름 매핑
    region_mapping = {
        # 특별시/광역시
        '서울': '서울특별시',
        '부산': '부산광역시',
        '대구': '대구광역시',
        '인천': '인천광역시',
        '광주': '광주광역시',
        '대전': '대전광역시',
        '울산': '울산광역시',
        '세종': '세종특별자치시',
        # 도
        '경기': '경기도',
        '강원': '강원도',
        '충북': '충청북도',
        '충남': '충청남도',
        '전북': '전라북도',
        '전남': '전라남도',
        '경북': '경상북도',
        '경남': '경상남도',
        '제주': '제주특별자치도'
    }
    
    # 입력된 지역명이 매핑 테이블에 있으면 변환, 없으면 원래 값 사용
    return region_mapping.get(first_word, first_word)

# 지역 컬럼 생성 및 변환
df["지역"] = df["충전소주소"].apply(convert_region_name)

# 지역별 충전소 수 계산
region_counts = df["지역"].value_counts().reset_index()
region_counts.columns = ["지역", "충전소 갯수"]

# 테이블 생성 (없는 경우)
cursor.execute("""
               CREATE TABLE IF NOT EXISTS ev_charger_status(
               region varchar(50),
               cnt int
               );
               """)

# 기존 데이터 삭제
cursor.execute("DELETE FROM ev_charger_status")
conn.commit()

# 새로운 데이터 삽입
region_counts  # 데이터 확인용 출력
insert_query = """
    INSERT INTO ev_charger_status (region, cnt)
    VALUES (%s, %s)
"""

data_to_insert = list(region_counts.itertuples(index=False, name=None))

# 데이터 삽입 실행
cursor.executemany(insert_query, data_to_insert)
conn.commit()


# 삽입된 데이터 확인
cursor.execute("SELECT * FROM ev_charger_status ORDER BY cnt DESC")
inserted_data = cursor.fetchall()
df_inserted = pd.DataFrame(inserted_data, columns=["지역", "충전소 갯수"])