# app.py
import streamlit as st
import pandas as pd
import pymysql
import altair as alt

# DB 연결
conn = pymysql.connect(
    host="localhost", user="root", password="root1234",
    db="6team", charset="utf8mb4"
)

# SQL 실행 (테이블에 region, count 컬럼 있다고 가정)
df = pd.read_sql("SELECT region, count FROM ev_charger_status", conn)
conn.close()

st.title("전기차 충전소 지역별 현황")

# Altair 막대그래프
chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("region:N", title="지역", sort="-y"),   # x축: 지역, 개수순 정렬
        y=alt.Y("count:Q", title="수량"),
        color=alt.Color("region:N", legend=None),       # 색상 자동 구분
        tooltip=["region", "count"]                     # 마우스오버 툴팁
    )
    .properties(width=600, height=400)
)

st.altair_chart(chart, use_container_width=True)

st.markdown(
    "<div style='text-align:right; font-size:12px; color:gray;'>출처: 한국전력공사 (2025.6.30) </div>",
    unsafe_allow_html=True
)

