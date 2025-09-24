# 🚗 EV(전기차) 현황 분석 및 전기차 브랜드 FAQ

---

## 🧑‍🤝‍🧑 팀 소개

   - 팀명 : hexa(헥사)
   - 팀원

| | | | |
|---|---|---|---|
| <img src="https://avatars.githubusercontent.com/u/181325754?v=4" width="120"> <br> [김태빈](https://github.com/binibini90) | <img src="https://avatars.githubusercontent.com/u/178726488?v=4" width="120"> <br> [김황현](https://github.com/python11021) | <img src="https://avatars.githubusercontent.com/u/174814422?v=4" width="120"> <br> [나호성](https://github.com/BBuSang) | <img src="https://avatars.githubusercontent.com/u/174813325?v=4" width="120"> <br> [이지은](https://github.com/jieun9508-cyber) |


---

## 📖 프로젝트 개요

   1. 프로젝트 명
      - 전기차 현황 보고
   2. 프로젝트 소개
      - 대체 에너지를 활용한 자동차의 수요가 높아지는 추세에 맞춰 그의 대표적인 예시인 전기 자동차의 등록 현황을 분석하여 대중의 관심을 확인하고 관련 인프라의 한계를 알아보기 위한 프로젝트
   3. 프로젝트 목표
      - 전기차 연도별, 지역별 등록대수를 알아보고 그와 관련된 전기차 충전소의 지역적 분포 및 브랜드 별 FAQ를 크롤링하여 데이터로 시각화
   4. 프로젝트 결과
      - 데이터를 시각화 하여 증가하는 전기차 수요를 확인하고 충전소의 개수를 보며 현재 한계점을 분석하고 이해 할 수 있다.

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
