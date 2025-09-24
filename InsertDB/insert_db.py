import os
import re
import pandas as pd
import pymysql
from dotenv import load_dotenv

# 환경변수 불러오기
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "6team" 

# CSV 불러오기
df = pd.read_csv("C:/Users/31799/Desktop/SKN20-1ST-6TEAM/crawling/ev_car_stats_full_with_header.csv")

# MySQL 연결
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    charset='utf8mb4',
    autocommit=True
)
cursor = conn.cursor()

# DB 생성 및 선택
cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;")
cursor.execute(f"USE {DB_NAME};")

# 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS ev_registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    count INT NOT NULL,
    UNIQUE KEY unique_year_region (year, region)
);
""") # 중복 방지를 위한 UNIQUE 제약조건 추가

# 데이터 전처리
def clean_year(year_str):
    year_str = str(year_str).split('\n')[0].strip() 
    year_str = year_str.split('(')[0].strip()  
    return year_str

def clean_count(count_str):
    if pd.isna(count_str):
        return 0
    count = re.findall(r'\d+', str(count_str).replace(',', ''))
    return int(count[0]) if count else 0

# 지역 컬럼 추출
regions = [col for col in df.columns if col not in ['연월', '계']]

# DB 삽입
for _, row in df.iterrows():
    year = clean_year(row['연월'])
    
    try:
        year_num = int(year)
        if year_num < 2019:
            continue  # 2019년 이상 데이터만
    except ValueError:
        continue 
    
    for region in regions:
        try:
            count = clean_count(row[region])
            sql = """
            INSERT INTO ev_registration (year, region, count)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE count = VALUES(count)
            """
            cursor.execute(sql, (year, region, count))
        except Exception as e:
            continue

conn.commit()
print("모든 변경사항 저장 완료")
cursor.close()
conn.close()
print("데이터베이스 연결 종료")
