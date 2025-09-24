from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Chrome 실행
driver = webdriver.Chrome()
driver.get("https://www.hyundai.com/kr/ko/e/customer/center/faq")
time.sleep(2)

try:
    questions = []
    answers = []

# 페이지내 div 블럭
    div_lists_url = '#app > div.contant-area > section > div.l-container-body > div > div.l-contents-mid > section > div > div:nth-child(3) > div.list-wrap > div'
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    div_lists =  soup.select(div_lists_url)

    for div in div_lists:
        title = div.find('span', class_ = 'list-content')
        questions.append(title.text)

        # print(questions)

# 버튼 리스트 가져오기
    buttons = driver.find_elements(By.CLASS_NAME, 'list-title')

    for button in buttons:
        # print("버튼 찾음:", button)

        # 버튼이 보이도록 스크롤 (화면 중앙 정렬)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(1)

        # 버튼 클릭 가능할 때까지 대기 후 클릭
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "list-title"))
        )

        # ActionChains로 강제 클릭
        actions = ActionChains(driver)
        actions.move_to_element(button).click().perform()
        time.sleep(0.5)

        # 클릭 후 숨겨진 내용 가져오기
        hidden_content = driver.find_element(By.CLASS_NAME, 'conts')
        # print(hidden_content.text)
        answers.append(hidden_content.text)



except Exception as e:
    print("오류 발생:", e)

finally:
    driver.quit()