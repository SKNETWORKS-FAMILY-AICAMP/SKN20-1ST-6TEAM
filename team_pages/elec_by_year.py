# 연도별 전기차 비율 변화 신규 생성.
# 2025.09.23 khh

import streamlit as st
import pandas as pd
import numpy as np
import elecdb   # 6team 디비 

# EV_REGISTRATION 테이블 연도별 전기차 현황 데이타 datas에 저장
datas =elecdb.elec_yearstatus_list()    

# x축: 연도, y축: 등록대수
df = pd.DataFrame({
    '연도': datas[0],
    '등록대수': datas[1]
})

x = datas[0]    # 연도
y = datas[1]    # 등록대수

df = pd.DataFrame({'연도': x, '등록대수': y})
df = df.set_index('연도')   # x축으로 쓸 컬럼을 인덱스로

st.title('연도별 전기차 비율 변화')
st.line_chart(df)