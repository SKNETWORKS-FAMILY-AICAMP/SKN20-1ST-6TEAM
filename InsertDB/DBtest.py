import pymysql
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# MySQL 서버 연결 (아직 DB는 선택하지 않음)
conn = pymysql.connect(
    host=host,
    user=user,
    password=password,
    charset='utf8mb4'
)

cursor = conn.cursor()

# 스키마 생성
cursor.execute("CREATE DATABASE IF NOT EXISTS `6team`;")
cursor.execute("USE `6team`;")

# 테이블 생성: 차량 통계용
cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicle_stats (
    year VARCHAR(10),
    fuel_type VARCHAR(20),
    count BIGINT
);
""")

# CSV 읽기
df = pd.read_csv("crawling/차량_연료_통계.csv", encoding='cp949')  # 한글 파일명 및 인코딩 설정

# wide 형태 -> long 형태 변환 (연도별, 연료별, 차량 수)
df_long = df.melt(id_vars=["연도"], var_name="fuel_type", value_name="count")

# 데이터 삽입
for _, row in df_long.iterrows():
    cursor.execute("""
        INSERT INTO vehicle_stats (year, fuel_type, count)
        VALUES (%s, %s, %s)
    """, (row["연도"], row["fuel_type"], row["count"]))

# 변경사항 저장 및 연결 종료
conn.commit()
conn.close()
