from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

# 크롬 드라이버 실행
driver = webdriver.Chrome()

# 사이트 접속
driver.get("https://chargeinfo.ksga.org/front/statistics/evCar")
time.sleep(3)  # 페이지 로딩 대기

# 헤더(th) 가져오기
headers = driver.find_elements(By.CSS_SELECTOR, "table thead tr th")
header_names = [h.text.strip() for h in headers]

# 표 데이터 가져오기
rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

data = []
for row in rows:
    cols = [col.text.strip() for col in row.find_elements(By.TAG_NAME, "td")]
    if cols:
        data.append(cols)

driver.quit()

# DataFrame 생성 (헤더 포함)
df = pd.DataFrame(data, columns=header_names)

# 확인
print(df.head())

# CSV 저장
df.to_csv("ev_car_stats_full_with_header.csv", index=False, encoding="utf-8-sig")
print("CSV 파일 저장 완료: ev_car_stats_full_with_header.csv")