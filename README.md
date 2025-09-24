# 🚗 EV FAQ Finder (전기차 FAQ 통합 검색 서비스)

## 📖 프로젝트 소개
EV(전기차) 이용자가 늘어나는 추이를 확인하고 ~~~~~~~~
저희 팀은 전기차의 등록현황과 전기차 등록 비율, 충전소 현황, **브랜드별 FAQ를 크롤링하여 데이터베이스에 저장하고, Streamlit 기반 웹 서비스에서 한눈에 조회할 수 있는 플랫폼**을 만들었습니다.  

👉 누구나 쉽게 EV 관련 FAQ를 검색하고 문제 해결에 도움을 받을 수 있습니다.

---

## 🧑‍🤝‍🧑 팀원 소개

- <img src="https://avatars.githubusercontent.com/u/181325754?v=4" width="80"> [김태빈](https://github.com/binibini90)  
- <img src="https://avatars.githubusercontent.com/u/178726488?v=4" width="80"> [김황현](https://github.com/python11021)  
- <img src="https://avatars.githubusercontent.com/u/174814422?v=4" width="80"> [나호성](https://github.com/BBuSang)  
- <img src="https://avatars.githubusercontent.com/u/174813325?v=4" width="80"> [이지은](https://github.com/jieun9508-cyber)  



---

## 🛠 기술 스택
- **언어/프레임워크**: Python, Streamlit, Selenium  
- **데이터베이스**: MySQL  
- **협업 도구**: GitHub,discord 

---

## 🚀 주요 기능
1. **전기차 등록현황 및 비중 분석**
   - 공식 웹사이트에서 정보 자동 수집
2. **전기차 충전소 배치 현황 수집**
   - 공식 웹사이트에서 정보 자동 수집
3. **브랜드별 FAQ 크롤링**
   - Kia, Hyundai 등 제조사 공식 웹사이트에서 FAQ 자동 수집
4. **DB 저장 및 관리**
   - MySQL에 연간 자동차 등록현황, 전기차 충전소 배치 현황, 질문/답변을 저장하여 통합 관리
5. **FAQ 검색 서비스**
   - Streamlit 웹앱에서 브랜드 선택 후 FAQ 조회 가능
   - 키워드 검색 기능 지원

---

## 📊 서비스 화면
| 메인 화면 | FAQ 조회 화면 |
|-----------|---------------|
| ![메인화면](images/main.png) | ![FAQ조회](images/faq.png) |

---

## ⚙️ 실행 방법
```bash
# 저장소 클론
git clone https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN20-1ST-6TEAM.git
cd SKN20-1ST-6TEAM

# 패키지 설치
pip install -r requirements.txt

# 실행
streamlit run app.py
