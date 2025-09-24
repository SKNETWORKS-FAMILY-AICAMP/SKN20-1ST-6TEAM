# DB 관련 import
import pymysql
import os
from dotenv import load_dotenv

# 환경변수 호출.
load_dotenv()

DB_NAME = "6team" 

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST")
        ,user=os.getenv("DB_USER")
        ,password=os.getenv("DB_PASSWORD")
        ,charset='utf8mb4'       # MySQL, MariaDB 데이터베이스(DB)에 연결할 때, 문자의 인코딩 방식을 지정하는 옵션
        ,database=DB_NAME
    )

# EV_REGISTRATION 테이블 연도별 전기차 현황 조회
def elec_yearstatus_list(isDict = False):
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

# EV_REGISTRATION 테이블 연도 데이타만 가져오기(셀렉트 박스용)
def year_list():
    result =[]  #연도를 담을 빈 리스트
    with get_connection() as conn:
        sql = 'SELECT YEAR FROM EV_REGISTRATION GROUP BY YEAR ORDER BY YEAR'   
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall() 
            result = [r[0] for r in rows]  
            print(result)        
        return result

# EV_REGISTRATION 테이블 지역별 전기차 현황 조회
def elec_year_region(sel_year):
    print(f"year {sel_year}")
    with get_connection() as conn:
        sql = "SELECT YEAR, REGION, COUNT FROM EV_REGISTRATION WHERE YEAR =%s"  
        region = [] # 지역
        count  = []  # 등록대수
        with conn.cursor() as cur:
            cur.execute(sql, sel_year)
            for c in cur.fetchall():            
                region.append(c[1])
                count.append(c[2])
        return region,count
    pass