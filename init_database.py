import os
import re
import time
import requests
import pandas as pd
import pymysql
import mysql.connector
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 환경변수 불러오기
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "6team"

def create_database():
    """데이터베이스 생성 및 초기화"""
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        charset='utf8mb4',
        autocommit=True
    )
    cursor = conn.cursor()

    # DB 재생성
    print("데이터베이스 초기화 중...")
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
    cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;")
    cursor.execute(f"USE {DB_NAME};")

    # 테이블 생성
    print("테이블 생성 중...")
    
    # 전기차 등록 현황 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ev_registration (
        id INT AUTO_INCREMENT PRIMARY KEY,
        year VARCHAR(50) NOT NULL,
        region VARCHAR(50) NOT NULL,
        count INT NOT NULL,
        UNIQUE KEY unique_year_region (year, region)
    );
    """)

    # FAQ 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INT AUTO_INCREMENT PRIMARY KEY,
        brand VARCHAR(50),
        question TEXT,
        answer TEXT
    );
    """)

    # 차량 통계 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicle_stats (
        year VARCHAR(10),
        fuel_type VARCHAR(20),
        count BIGINT
    );
    """)

    # 충전소 현황 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ev_charger_status (
        region VARCHAR(50),
        count INT
    );
    """)

    cursor.close()
    conn.close()
    print("데이터베이스 및 테이블 생성 완료")

def insert_ev_registration_data():
    """전기차 등록 현황 데이터 삽입"""
    print("전기차 등록 현황 데이터 삽입 중...")
    
    # CSV 불러오기
    df = pd.read_csv("crawling/ev_car_stats_full_with_header.csv")
    
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    def clean_year(year_str):
        year_str = str(year_str).split('\n')[0].strip() 
        year_str = year_str.split('(')[0].strip()  
        return year_str

    def clean_count(count_str):
        if pd.isna(count_str):
            return 0
        count = re.findall(r'\d+', str(count_str).replace(',', ''))
        return int(count[0]) if count else 0

    regions = [col for col in df.columns if col not in ['연월', '계']]
    
    for _, row in df.iterrows():
        year = clean_year(row['연월'])
        try:
            year_num = int(year)
            if year_num < 2019:
                continue
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
                print(f"Error inserting data for {year}, {region}: {e}")
                continue

    conn.commit()
    cursor.close()
    conn.close()
    print("전기차 등록 현황 데이터 삽입 완료")

def insert_vehicle_stats():
    """차량 통계 데이터 삽입"""
    print("차량 통계 데이터 삽입 중...")
    
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    # CSV 읽기
    df = pd.read_csv("crawling/차량_연료_통계.csv", encoding='cp949')
    df_long = df.melt(id_vars=["연도"], var_name="fuel_type", value_name="count")

    for _, row in df_long.iterrows():
        cursor.execute("""
            INSERT INTO vehicle_stats (year, fuel_type, count)
            VALUES (%s, %s, %s)
        """, (row["연도"], row["fuel_type"], row["count"]))

    conn.commit()
    cursor.close()
    conn.close()
    print("차량 통계 데이터 삽입 완료")

def insert_charger_status():
    """충전소 현황 데이터 삽입"""
    print("충전소 현황 데이터 수집 및 삽입 중...")
    
    API_URL = "https://api.odcloud.kr/api/15039545/v1/uddi:f8f879ad-68cf-40fb-8ccc-cb36eaf1baca"
    SERVICE_KEY = "8ae9566a50f6b632198d0863de24d4fdb8a0491b5ad384b8d83a7302a3c00ba9"

    res = requests.get(API_URL, params={
        "serviceKey": SERVICE_KEY,
        "page": 1,
        "perPage": 1000,
        "returnType": "JSON"
    })
    
    data = res.json()["data"]
    df = pd.DataFrame(data)

    def convert_region_name(address):
        first_word = address.split()[0]
        region_mapping = {
            '서울': '서울특별시', '부산': '부산광역시', '대구': '대구광역시',
            '인천': '인천광역시', '광주': '광주광역시', '대전': '대전광역시',
            '울산': '울산광역시', '세종': '세종특별자치시', '경기': '경기도',
            '강원': '강원도', '충북': '충청북도', '충남': '충청남도',
            '전북': '전라북도', '전남': '전라남도', '경북': '경상북도',
            '경남': '경상남도', '제주': '제주특별자치도'
        }
        return region_mapping.get(first_word, first_word)

    df["지역"] = df["충전소주소"].apply(convert_region_name)
    region_counts = df["지역"].value_counts().reset_index()
    region_counts.columns = ["지역", "충전소 갯수"]

    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ev_charger_status")
    
    insert_query = "INSERT INTO ev_charger_status (region, count) VALUES (%s, %s)"
    data_to_insert = list(region_counts.itertuples(index=False, name=None))
    cursor.executemany(insert_query, data_to_insert)

    conn.commit()
    cursor.close()
    conn.close()
    print("충전소 현황 데이터 삽입 완료")

def insert_faq_data():
    """FAQ 데이터 삽입"""
    print("FAQ 데이터 삽입 중...")
    
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    # 현대 FAQ 데이터
    hyundai_faqs = [
        (
            "Hyundai",
            "전기차는 주행 가능 거리가 짧다?",
            """걱정마세요. 전기차 주행 가능 거리는 대다수 운전자의 일일 주행 거리보다 훨씬 깁니다.
- 서울–부산 최적 경로: 400km
- 아이오닉 6 주행 가능 거리: 524km
따라서 단 1회 충전으로도 서울부터 부산까지 주행 가능합니다.
* IONIQ6 Long Range 2WD, 18인치 기준"""
        ),
        (
            "Hyundai",
            "전기차는 위험하다?",
            """오해입니다. 현대자동차 전기차의 고전압 배터리는 방진/방수 설계로 1m 수심에서도 30분간 물이 유입되지 않습니다.
또한 사고 등으로 기밀이 파괴되어도 배터리 매니지먼트 시스템이 작동해 파워 릴레이를 즉시 끊어 고전압을 차단하므로 물에 빠져도 감전 걱정이 없습니다."""
        ),
        (
            "Hyundai",
            "전기차 배터리는 수명이 짧다?",
            """아닙니다. 현대자동차 전기차는 주행 거리 최대 20만 km까지 배터리 품질을 보증합니다.
따라서 몇 년 뒤에도 안심하고 전기차를 이용하실 수 있습니다."""
        ),
        (
            "Hyundai",
            "전기차는 전자파가 강하다?",
            """오해입니다. 국립전파연구원에 따르면 전기차 충전 시 발생 전자파는 인체보호 기준 대비 0.5% 수준입니다.
비교:
- 전기 면도기: 1.59%
- 컴퓨터: 0.54%
- 전기차 충전 시: 0.5%
즉, 주변 기기와 유사한 수준입니다."""
        ),
        (
            "Hyundai",
            "비 오는 날 충전하면 위험하다?",
            """위험하지 않습니다. 비가 와서 충전구 내부로 액체가 들어가도 배수 구조로 배출되므로 감전 걱정이 없습니다.
또한 충전소의 충전기에도 절연 처리 및 방수 설계가 철저히 적용되어 있어 안심하고 이용하세요."""
        ),
    ]

    # 현대 FAQ 저장
    cursor.executemany(
        "INSERT INTO faq (brand, question, answer) VALUES (%s, %s, %s)",
        hyundai_faqs
    )
    conn.commit()
    print("현대 FAQ 데이터 삽입 완료")

    # 기아 FAQ 크롤링 및 저장
    print("기아 FAQ 데이터 크롤링 중...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.kia.com/kr/vehicles/kia-ev/guide/faq")

    wait = WebDriverWait(driver, 10)
    faq_buttons = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".cmp-accordion__button"))
    )

    for i, btn in enumerate(faq_buttons):
        try:
            question = btn.text.strip()
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.5)

            panel_id = f"accordion-item-{i}-panel"
            panel = wait.until(
                EC.visibility_of_element_located((By.ID, panel_id))
            )

            answer = panel.text.strip()
            if not answer:
                answer = "내용 없음"
            
            cursor.execute(
                "INSERT INTO faq (brand, question, answer) VALUES (%s, %s, %s)",
                ("Kia", question, answer)
            )
            conn.commit()
        except Exception as e:
            print(f"[에러] {i}번 질문 처리 실패: {e}")
            continue

    driver.quit()
    cursor.close()
    conn.close()
    print("기아 FAQ 데이터 삽입 완료")

def main():
    """전체 데이터베이스 초기화 및 데이터 삽입 실행"""
    try:
        create_database()
        insert_ev_registration_data()
        insert_vehicle_stats()
        insert_charger_status()
        insert_faq_data()
        print("✅ 모든 데이터 초기화 및 삽입 완료")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()