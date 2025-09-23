# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

url = 'https://chargeinfo.ksga.org/front/statistics/evCar'
# 웹 드라이버를 자동으로 설치하고 최신버전을 유지
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 사이트 접속
driver.get(url)
# driver.maximize_window() # 전체 화면으로 실행  옵션
print('사이트 접속했습니다.')
# 사이트가 로드될때까지 기다린다.
time.sleep(3)

# BeautifulSoup으로 현재 페이지 파싱
soup = BeautifulSoup(driver.page_source, 'html.parser')

# 테이블 선택
table = soup.select_one("table.datatable")

# 테이블 행 가져오기 (thead 제외하고 tbody만)
rows = table.select("tbody tr")

# 각 행의 열(td) 데이터 추출
for row in rows:
    cols = [col.get_text(strip=True) for col in row.select("td")]
    print(cols)

# 크롬 드라이버 종료
driver.quit()
