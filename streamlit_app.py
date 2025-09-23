import os
import math
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import streamlit as st

# ── .env 로드
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

st.set_page_config(page_title="EV FAQ 뷰어", page_icon="⚡", layout="wide")
st.title("⚡ EV FAQ 뷰어")

# ── DB 연결(캐시). 캐시에 얹을 때 env 값이 키로 들어가게 해서 잘못된 캐시 재사용 방지
@st.cache_resource(show_spinner=False)
def get_conn_cached(host, user, password, db):
    conn = mysql.connector.connect(
        host=host, user=user, password=password, database=db
    )
    return conn

def get_conn():
    conn = get_conn_cached(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    try:
        # 끊겼으면 자동 재연결
        conn.ping(reconnect=True, attempts=1, delay=0)
    except Error:
        # 혹시 모를 재생성 (캐시 무효화가 어려우니 강제로 재연결)
        return get_conn_cached(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    return conn

def fetch_brands():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT brand FROM faq ORDER BY brand")
    brands = [r[0] for r in cur.fetchall()]
    cur.close()            # ✅ 커서는 닫되
    # conn.close()         # ❌ 커넥션은 닫지 마세요(캐시됨)
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

# ── 사이드바
with st.sidebar:
    st.subheader("🔎 검색/옵션")
    keyword = st.text_input("키워드 (질문/답변)")
    page_size = st.selectbox("페이지 크기", [10, 20, 50], index=1)
    st.caption("데이터는 DB로부터 읽기 전용입니다.")

# ── 브랜드 로드
try:
    brands = fetch_brands()
except Error as e:
    st.error(f"DB 연결/확인 실패: {e}")
    st.stop()

if not brands:
    st.info("브랜드 데이터가 없습니다. 먼저 faq_hyundai.py / faq_kia.py로 데이터를 적재하세요.")
    st.stop()

brand = st.radio("브랜드 선택", options=brands, horizontal=True)

# ── 카운트 & 페이지
try:
    total = count_faqs(brand, keyword)
except Error as e:
    st.error(f"브랜드 조회 실패: {e}")
    st.stop()

st.write(f"**{brand}** FAQ: {total}건")

if total == 0:
    st.info("검색 결과가 없습니다.")
else:
    pages = math.ceil(total / page_size)
    page = st.slider("페이지", 1, max(pages, 1), 1) if pages > 1 else 1
    offset = (page - 1) * page_size

    view_mode = st.radio("보기 방식", ["목록(접기)", "표 보기"], horizontal=True)
    rows = fetch_faqs(brand, keyword, limit=page_size, offset=offset)

    if view_mode == "표 보기":
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        for r in rows:
            with st.expander(f"Q. {r['question']}", expanded=False):
                st.write(r["answer"])

    if pages > 1:
        st.caption(f"페이지 {page}/{pages} · {page_size}개씩 보기")
