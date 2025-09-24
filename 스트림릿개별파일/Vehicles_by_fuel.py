import streamlit as st
import pandas as pd
import pymysql
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 예시
font_prop = fm.FontProperties(fname=font_path)

plt.rcParams['font.family'] = font_prop.get_name()

from dotenv import load_dotenv
load_dotenv()

# ----------------------------
# MySQL 연결
# ----------------------------
conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset='utf8mb4'
)
with st.sidebar:
    st.title("전기차 통계 분석")
    selected_menu = st.radio(
        "원하시는 분석을 선택하세요:",
        ["연료별 차량 수", "전기차 비율"]
    )
# 연도 + 연료별 차량 수 데이터 가져오기
query = "SELECT * FROM vehicle_stats;"
df = pd.read_sql(query, conn)
conn.close()

# wide 형태로 변환
df_wide = df.pivot(index='year', columns='fuel_type', values='count')

# 열 순서 재정렬 (원하는 순서대로 연료 타입을 나열)
desired_order = ['휘발유', '경유', 'LPG', '하이브리드', '전기', '수소'] 
df_wide = df_wide[desired_order]

# Streamlit 앱
st.title("차량 연료별 통계 분석")

# ----------------------------
# 1. 연료별 스택드 바 차트
# ----------------------------
def fuel_chart():

    st.subheader("연도별 연료별 차량 수 변화 (스택드 바)")
    # 그래프 크기 설정
    fig1, ax1 = plt.subplots(figsize=(12,7))
    
    # 비율 계산
    df_pct = df_wide.div(df_wide.sum(axis=1), axis=0) * 100
    
    # 스택 바 플롯
    ax1.clear()  # 이전 플롯 지우기
    bottoms = np.zeros(len(df_wide))
    
    # 각 연료 타입별로 바 그리기
    for column in df_wide.columns:
        values = df_wide[column]
        percentages = df_pct[column]
        bars = ax1.bar(df_wide.index, values, bottom=bottoms, label=column)
        
        # 비율 텍스트 추가
        for i, (bar, pct) in enumerate(zip(bars, percentages)):
            if pct >= 1:  # 1% 이상인 경우만 표시
                height = bar.get_height()
                text_y = bottoms[i] + height/2
                ax1.text(i, text_y, f'{pct:.1f}%',
                        ha='center', va='center',
                        fontsize=14, color='white',
                        fontweight='bold')
        bottoms += values
    
    ax1.set_xlabel("연도")
    ax1.set_ylabel("차량 수")
    plt.xticks(rotation=45)
    # 범례를 그래프 오른쪽으로 이동
    plt.legend(title="연료 종류", bbox_to_anchor=(1.15, 1), loc='upper left')
    # 그래프 여백 조정
    plt.tight_layout()
    
    st.pyplot(fig1)
    
    st.write("데이터 표")
    st.write(df.sort_values(by='year'))
    
# ----------------------------
# 2. 전기차와 전체 차량 비교 (혼합 차트)
# ----------------------------
def electric_ratio_chart():
    st.subheader("연도별 전기차 비율 vs 전체 차량 수 (혼합 차트)")
    df_wide['Total'] = df_wide.sum(axis=1)
    df_wide['Electric_ratio'] = df_wide['전기'] / df_wide['Total'] * 100

    fig2, ax2 = plt.subplots(figsize=(10,6))
    ax2.bar(df_wide.index, df_wide['Total'], color='skyblue', label='총 차량 수')
    ax2.set_xlabel('연도')
    ax2.set_ylabel('총 차량 수')
    ax2.tick_params(axis='y')

    ax3 = ax2.twinx()
    ax3.plot(df_wide.index, df_wide['Electric_ratio'], color='red', marker='o', label='전기차 비율 (%)')
    ax3.set_ylabel('전기차 비율 (%)', color='red')
    ax3.tick_params(axis='y')

    # 범례 추가
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax3.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    fig2.tight_layout()
    st.pyplot(fig2)

    # 전기차 비율 데이터 테이블 표시
    st.subheader("연도별 전기차 통계")
    ratio_df = pd.DataFrame({
        '연도': df_wide.index,
        '전기차 수': df_wide['전기'],
        '총 차량 수': df_wide['Total'],
        '전기차 비율(%)': df_wide['Electric_ratio'].round(2)
    }).sort_values('연도', ascending=True)
    
    # 데이터프레임 스타일링 및 표시
    st.dataframe(ratio_df.style.format({
        '전기차 수': '{:,.0f}',
        '총 차량 수': '{:,.0f}',
        '전기차 비율(%)': '{:.2f}%'
    }))

# 선택된 메뉴에 따른 차트 표시
if selected_menu == "연료별 차량 수":
    fuel_chart()
elif selected_menu == "전기차 비율":
    electric_ratio_chart()
