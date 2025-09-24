import os
import math
import mysql.connector
from mysql.connector import Error
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.express as px
import altair as alt
from dotenv import load_dotenv
import InsertDB.elecdb as elecdb  # 전기차 데이터베이스 모듈

# ─────────────────────────────────────────────────────────
# 기본 설정
# ─────────────────────────────────────────────────────────
# 폰트 설정
import platform

def set_font():
    if platform.system() == 'Darwin':  # macOS
        plt.rcParams['font.family'] = 'AppleGothic'
    elif platform.system() == 'Windows':
        plt.rcParams['font.family'] = 'Malgun Gothic'
    
    # 그래프에서 마이너스 기호가 깨지는 것을 방지
    plt.rcParams['axes.unicode_minus'] = False

set_font()

# 페이지 설정
st.set_page_config(
    page_title="전기차 종합 대시보드",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': '© 2025 전기차 종합 대시보드 - SK Networks',
        'Get help': 'mailto:support@example.com',
        'Report a bug': "mailto:bug@example.com"
    }
)

# 헤더/메트릭을 함수로 분리

def show_home():
    # DB에서 최신 연도와 직전 연도 데이터 조회
    conn = get_conn()
    # 전기차 등록대수
    reg_df = pd.read_sql("SELECT year, SUM(count) as total FROM ev_registration GROUP BY year ORDER BY year DESC LIMIT 2", conn)
    if len(reg_df) == 2:
        latest_year = reg_df.iloc[0]['year']
        latest_total = reg_df.iloc[0]['total']
        prev_total = reg_df.iloc[1]['total']
        reg_delta = latest_total - prev_total
        reg_rate = (reg_delta / prev_total * 100) if prev_total else 0
    else:
        latest_year = "-"
        latest_total = 0
        reg_delta = 0
        reg_rate = 0
    # 충전소 수
    charger_df = pd.read_sql("SELECT region, SUM(count) as total FROM ev_charger_status GROUP BY region", conn)
    charger_total = charger_df['total'].sum()
    # 충전소 전년 대비 증가율 (예시: ev_charger_status에 연도 정보가 없으면 계산 불가)
    # 실제 연도별 데이터가 있으면 아래처럼 쿼리
    # charger_year_df = pd.read_sql("SELECT year, SUM(count) as total FROM ev_charger_status GROUP BY year ORDER BY year DESC LIMIT 2", conn)
    # ... 증가율 계산 ...
    charger_rate = "-"  # 연도별 데이터 없으면 표시 불가
    conn.close()

    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/4378/4378534.png", width=100)
        st.title("⚡ 전기차 종합 대시보드")
        st.caption("전기차의 현재와 미래를 한눈에 살펴보세요")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"전년 대비 증가율 ({latest_year})", value=f"{reg_rate:.1f}%", delta=f"{reg_delta:,}대")
    with col2:
        st.metric(label="전기차 총 등록대수", value=f"{int(latest_total):,}대", delta=f"{int(reg_delta):,}대")
    with col3:
        st.metric(label="충전소 총 수", value=f"{int(charger_total):,}개")
    st.divider()

# .env 로드 & 환경변수
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# ─────────────────────────────────────────────────────────
# DB 연결 (Streamlit 캐시)
# ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_conn_cached(host, user, password, db):
    conn = mysql.connector.connect(
        host=host, user=user, password=password, database=db,
        charset='utf8mb4'
    )
    return conn

def get_conn():
    """캐시된 커넥션을 가져오고 끊겼으면 재연결."""
    conn = get_conn_cached(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    try:
        conn.ping(reconnect=True, attempts=1, delay=0)
    except Error:
        return get_conn_cached(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    return conn

# ─────────────────────────────────────────────────────────
# 충전소 현황 관련 함수
# ─────────────────────────────────────────────────────────
def charger_status_chart():
    # DB 연결해서 데이터 가져오기
    conn = get_conn()
    df = pd.read_sql("SELECT region, count FROM ev_charger_status", conn)
    
    st.header("전기차 충전소 지역별 현황")
    
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

# ─────────────────────────────────────────────────────────
# FAQ 관련 쿼리 함수
# ─────────────────────────────────────────────────────────
def fetch_brands():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT brand FROM faq ORDER BY brand")
    brands = [r[0] for r in cur.fetchall()]
    cur.close()
    return brands

def count_faqs(brand, keyword=None):
    conn = get_conn()
    cur = conn.cursor()
    sql = "SELECT COUNT(*) FROM faq WHERE brand = %s"
    params = [brand]
    if keyword:
        sql += " AND (question LIKE %s OR answer LIKE %s)"
        params += [f"%{keyword}%", f"%{keyword}%"]
    cur.execute(sql, params)
    n = cur.fetchone()[0]
    cur.close()
    return n

def fetch_faqs(brand, keyword=None, limit=20, offset=0):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql = "SELECT id, question, answer FROM faq WHERE brand = %s"
    params = [brand]
    if keyword:
        sql += " AND (question LIKE %s OR answer LIKE %s)"
        params += [f"%{keyword}%", f"%{keyword}%"]
    sql += " ORDER BY id DESC LIMIT %s OFFSET %s"
    params += [limit, offset]
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return rows

# ─────────────────────────────────────────────────────────
# 차량 통계 관련 함수
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_vehicle_stats():
    conn = get_conn()
    query = "SELECT * FROM vehicle_stats;"
    df = pd.read_sql(query, conn)
    
    # wide 형태로 변환
    df_wide = df.pivot(index='year', columns='fuel_type', values='count')
    
    # 열 순서 재정렬
    desired_order = ['휘발유', '경유', 'LPG', '하이브리드', '전기', '수소']
    df_wide = df_wide[desired_order]
    
    return df, df_wide

def fuel_chart():
    df, df_wide = load_vehicle_stats()
    
    st.subheader("연도별 연료별 차량 수 변화 (스택드 바)")
    fig1, ax1 = plt.subplots(figsize=(12,7))
    
    # 비율 계산
    df_pct = df_wide.div(df_wide.sum(axis=1), axis=0) * 100
    
    # 스택 바 플롯
    ax1.clear()
    bottoms = np.zeros(len(df_wide))
    
    for column in df_wide.columns:
        values = df_wide[column]
        percentages = df_pct[column]
        bars = ax1.bar(df_wide.index, values, bottom=bottoms, label=column)
        
        for i, (bar, pct) in enumerate(zip(bars, percentages)):
            if pct >= 1:
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
    plt.legend(title="연료 종류", bbox_to_anchor=(1.15, 1), loc='upper left')
    plt.tight_layout()
    
    st.pyplot(fig1)
    
    st.write("데이터 표")
    st.write(df.sort_values(by='year'))

def electric_ratio_chart():
    df, df_wide = load_vehicle_stats()
    
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

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax3.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    fig2.tight_layout()
    st.pyplot(fig2)

    st.subheader("연도별 전기차 통계")
    ratio_df = pd.DataFrame({
        '연도': df_wide.index,
        '전기차 수': df_wide['전기'],
        '총 차량 수': df_wide['Total'],
        '전기차 비율(%)': df_wide['Electric_ratio'].round(2)
    }).sort_values('연도', ascending=True)
    
    st.dataframe(ratio_df.style.format({
        '전기차 수': '{:,.0f}',
        '총 차량 수': '{:,.0f}',
        '전기차 비율(%)': '{:.2f}%'
    }))

# ─────────────────────────────────────────────────────────
# 메인 UI
# ─────────────────────────────────────────────────────────
st.title("⚡ 전기차 종합 대시보드")

# 사이드바 - 메뉴 선택
with st.sidebar:
    st.title("메뉴 선택")
    
    st.markdown("---")
    # 메뉴 선택
    main_menu = st.radio(
        "보고 싶은 정보를 선택하세요:",
        ["홈", "연도별 전기차 현황", "지역별 전기차 현황", "연료별 차량 수", 
         "전기차 비율", "충전소 현황", "브랜드별 FAQ"]
    )
    
    # 프로필 카드
    st.markdown("---")
    st.subheader("📊 대시보드 정보")
    st.info("""
    - 최근 업데이트: 2025.09.24
    - 데이터 출처: 한국전력공사
    - API 버전: v1.0.0
    """)

    # 하단 정보
    st.markdown("---")
    st.caption("© 2025 SK Networks. All rights reserved.")

# ─────────────────────────────────────────────────────────
# 연도별/지역별 전기차 현황 관련 함수
# ─────────────────────────────────────────────────────────
def yearly_ev_chart():
    # 연도별 전기차 현황 데이터 가져오기
    datas = elecdb.elec_yearstatus_list()
    
    # 데이터프레임 생성
    df = pd.DataFrame({
        '연도': datas[0],
        '등록대수': datas[1]
    })
    df = df.set_index('연도')
    
    st.header('연도별 전기차 등록 현황')
    st.line_chart(df)

def regional_ev_chart():
    st.header("지역별 전기차 보급 현황")
    
    # 연도 목록 가져오기
    sel_year = elecdb.year_list()
    selected_year = st.selectbox("연도를 선택하세요", sel_year, index=len(sel_year)-1)
    
    # 선택된 연도의 지역별 데이터 가져오기
    map_data = elecdb.elec_year_region(selected_year)
    
    # 지역 정보 매핑
    region_info = {
        '경북': {'lat': 37.8228, 'lon': 128.1555},
        '경기': {'lat': 37.4138, 'lon': 127.5183},
        '대구': {'lat': 35.4606, 'lon': 128.2132},
        '강원': {'lat': 36.5769, 'lon': 128.5051},
        '광주': {'lat': 35.1595, 'lon': 126.8526},
        '경남': {'lat': 35.8722, 'lon': 128.6025},
        '대전': {'lat': 36.3504, 'lon': 127.3845},
        '부산': {'lat': 35.1796, 'lon': 129.0756},
        '서울': {'lat': 37.5665, 'lon': 126.9780},
        '충북': {'lat': 36.4801, 'lon': 127.2890},
        '울산': {'lat': 35.5384, 'lon': 129.3114},
        '인천': {'lat': 37.4563, 'lon': 126.7052},
        '전남': {'lat': 34.8679, 'lon': 126.9910},
        '충남': {'lat': 35.8204, 'lon': 127.1087},
        '제주': {'lat': 33.4996, 'lon': 126.5312},
        '전북': {'lat': 36.5184, 'lon': 126.8000},
        '세종': {'lat': 36.6356, 'lon': 127.4917}
    }
    
    # 데이터프레임 생성을 위한 리스트 준비
    regions = map_data[0]
    lats = []
    lons = []
    
    # 각 지역에 대한 위도/경도 매핑
    for region in regions:
        if region in region_info:
            lats.append(region_info[region]['lat'])
            lons.append(region_info[region]['lon'])
        else:
            st.warning(f"'{region}' 지역의 좌표 정보가 없습니다.")
            lats.append(35.907757)  # 한국 중심 위도
            lons.append(127.766922)  # 한국 중심 경도
    
    # 지도 데이터 준비
    df = pd.DataFrame({
        'regions': regions,
        'lats': lats,
        'lons': lons,
        'pop': map_data[1]
    })
    
    # 지도 생성
    fig = px.scatter_mapbox(
        df,
        lat="lats",
        lon="lons",
        hover_name="regions",
        hover_data={'pop': True, 'lats': False, 'lons': False},
        size="pop",
        color="regions",
        zoom=6,
        height=800,
        mapbox_style="open-street-map"
    )
    
    st.plotly_chart(fig)

# 메인 컨텐츠
if main_menu == "홈":
    show_home()
elif main_menu == "연도별 전기차 현황":
    yearly_ev_chart()
elif main_menu == "지역별 전기차 현황":
    regional_ev_chart()
elif main_menu == "연료별 차량 수":
    st.header("차량 연료별 통계 분석")
    fuel_chart()
elif main_menu == "전기차 비율":
    st.header("전기차 비율 분석")
    electric_ratio_chart()
elif main_menu == "충전소 현황":
    charger_status_chart()
else:  # FAQ 섹션
    try:
        brands = fetch_brands()
    except Error as e:
        st.error(f"DB 연결/확인 실패: {e}")
        st.stop()

    if not brands:
        st.info("브랜드 데이터가 없습니다. 먼저 FAQ 데이터를 적재하세요.")
        st.stop()

    brand = st.radio("브랜드 선택", options=brands, horizontal=True)

    try:
        total = count_faqs(brand)  # keyword 제거
    except Error as e:
        st.error(f"브랜드 조회 실패: {e}")
        st.stop()

    st.write(f"**{brand}** FAQ: {total}건")

    if total == 0:
        st.info("FAQ 데이터가 없습니다.")
    else:
        default_page_size = 20
        pages = math.ceil(total / default_page_size)
        page = st.slider("페이지", 1, max(pages, 1), 1) if pages > 1 else 1
        offset = (page - 1) * default_page_size

        rows = fetch_faqs(brand, limit=default_page_size, offset=offset)  # keyword 제거

        for r in rows:
            with st.expander(f"Q. {r['question']}", expanded=False):
                st.write(r["answer"])

        if pages > 1:
            st.caption(f"페이지 {page}/{pages} · {default_page_size}개씩 보기")