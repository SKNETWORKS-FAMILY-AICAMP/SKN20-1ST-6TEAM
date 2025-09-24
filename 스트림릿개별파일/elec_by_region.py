# 지역별 전기차 비율 변화 신규 생성.
# 2025.09.23 khh

import streamlit as st
import pandas as pd
import plotly.express as px
import InsertDB.elecdb as elecdb


st.title("지역별 전기차 보급 현황")
# EV_REGISTRATION 테이블 연도 데이타만 가져오기
sel_year =elecdb.year_list()  

print(sel_year)
selected_year = st.selectbox("연도를 선택하세요", sel_year, index=len(sel_year)-1)

print(f'selected_year {selected_year}')
map_data = elecdb.elec_year_region(selected_year)

print(f'map_data {map_data}')
# lats : 위도 lons : 경도
df = pd.DataFrame({
    'regions':map_data[0],
    'lats':[37.8228, 37.4138, 35.4606, 36.5769, 35.1595, 35.8722, 36.3504, 35.1796,
            37.5665, 36.4801, 35.5384, 37.4563, 34.8679, 35.8204, 33.4996, 36.5184, 36.6356],
    'lons':[128.1555, 127.5183, 128.2132, 128.5051, 126.8526, 128.6025, 127.3845, 129.0756,
            126.9780, 127.2890, 129.3114, 126.7052, 126.9910, 127.1087, 126.5312, 126.8000, 127.4917],
    'pop':map_data[1]
})

fig = px.scatter_mapbox(
    df,
    lat="lats",
    lon="lons",
    hover_name="regions",
    hover_data={'pop': True, 'lats': False, 'lons': False},
    size="pop",                   # 등록댓수에 따라 마커 크기 달라짐
    color="regions",               # 지역별 색상
    zoom=6,
    height=800,
    mapbox_style="open-street-map"
)


# 4. 셀렉트박스를 마지막에 출력 (타이틀/차트 아래)

st.plotly_chart(fig)

