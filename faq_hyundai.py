import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = conn.cursor()

# 테이블 없으면 생성
cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INT AUTO_INCREMENT PRIMARY KEY,
        brand VARCHAR(50),
        question TEXT,
        answer TEXT
    )
""")

# 현대 Q&A 데이터
faqs = [
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

# 일괄 저장
cursor.executemany(
    "INSERT INTO faq (brand, question, answer) VALUES (%s, %s, %s)",
    faqs
)
conn.commit()

print(f"✅ 저장 완료: {cursor.rowcount}건")

cursor.close()
conn.close()
