import pandas as pd

# 파일 경로 지정
file_path = "차량_연료_통계.csv"  # CSV 파일이 현재 폴더에 있는 경우
# 또는 절대 경로 사용
# file_path = r"C:\Users\31799\Desktop\SKN20-1ST-6TEAM\차량_연료_통계.csv"

# CSV 읽기 (한글 파일을 위한 인코딩 변경)
df = pd.read_csv(file_path, encoding='cp949')  # 또는 'euc-kr' 시도

# 상위 5개 데이터 확인
print(df)
