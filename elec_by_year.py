# 연도별 전기차 비율 변화 신규 생성.
# 2025.09.23 khh

import streamlit as st
import pandas as pd
import numpy as np
# DB 관련 import
import pymysql
import os
from dotenv import load_dotenv

# 환경변수 호출.
load_dotenv()


DB_NAME = "6team" 

# db 연결
# 1. .env 파일 데이타 불러오기 & DB 연결 
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST")
        ,user=os.getenv("DB_USER")
        ,password=os.getenv("DB_PASSWORD")
        ,charset='utf8mb4'       # MySQL, MariaDB 데이터베이스(DB)에 연결할 때, 문자의 인코딩 방식을 지정하는 옵션
        ,database=DB_NAME
    )

# EV_REGISTRATION 테이블 연도별 전기차 현황 조회
def elec_year_list(isDict = False):
    with get_connection() as conn:
        sql = '''
                SELECT YEAR
                     ,SUM(COUNT) AS SUM_YEAR
                  FROM EV_REGISTRATION
                GROUP BY YEAR 
              '''   
        x = []
        y = []
        with conn.cursor() as cur:
            cur.execute(sql)
            for c in cur.fetchall():            
                x.append(c[0])
                y.append(int(c[1]))
        return x,y

# EV_REGISTRATION 테이블 연도별 전기차 현황 데이타 datas에 저장
datas =elec_year_list()    

# x축: 연도, y축: 등록대수
df = pd.DataFrame({
    '연도': datas[0],
    '등록대수': datas[1]
})

print(datas)

x = datas[0]    # 연도
y = datas[1]    # 등록대수

df = pd.DataFrame({'연도': x, '등록대수': y})
df = df.set_index('연도')   # x축으로 쓸 컬럼을 인덱스로

st.title('연도별 전기차 비율 변화')
st.line_chart(df)