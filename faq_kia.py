import os
import time
import mysql.connector
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. 환경 변수 불러오기
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# 2. MySQL 연결 및 테이블 생성
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INT AUTO_INCREMENT PRIMARY KEY,
        brand VARCHAR(50),
        question TEXT,
        answer TEXT
    )
""")

# 3. Selenium 설정
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://www.kia.com/kr/vehicles/kia-ev/guide/faq")

wait = WebDriverWait(driver, 10)

# 4. FAQ 버튼 모두 가져오기
faq_buttons = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".cmp-accordion__button"))
)

print(f"FAQ 개수: {len(faq_buttons)}")

# 5. 각 FAQ 클릭 → 질문/답변 수집
for i, btn in enumerate(faq_buttons):
    try:
        question = btn.text.strip()
        
        # 버튼 클릭
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)

        # 패널 ID 구성
        panel_id = f"accordion-item-{i}-panel"

        # 패널 안의 답변 대기
        panel = wait.until(
            EC.visibility_of_element_located((By.ID, panel_id))
        )

        # 답변 전체 텍스트 추출 (줄바꿈 포함)
        answer = panel.text.strip()
        if not answer:
            answer = "내용 없음"
        
        # MySQL 저장
        sql = """
            INSERT INTO faq (brand, question, answer)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, ("Kia", question, answer))
        conn.commit()

        print(f"[저장 완료] Q: {question[:20]}...")

    except Exception as e:
        print(f"[에러] {i}번 질문 처리 실패: {e}")
        continue

# 마무리
driver.quit()
cursor.close()
conn.close()
print("✅ 모든 FAQ 크롤링 및 저장 완료")
