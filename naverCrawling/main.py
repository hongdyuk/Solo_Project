from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pymysql
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from restaurant_list.list import RESTAURANT_LIST

NAVER_PLACE_URL = "https://map.naver.com/p?c=15.00,0,0,0,dh"

# 크롤링이 완료된 블로그 url_list
BLOG_URL_LIST = []

BROWSER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

for i in RESTAURANT_LIST:
    try:
        # 네이버 플레이스 홈화면을 브라우저로 띄움
        BROWSER.get(NAVER_PLACE_URL)
        print(f'지금은 다음 가게를 검색 중 입니다.: {i}')

        # 검색창 찾기
        search = BROWSER.find_element(By.CLASS_NAME, "input_search")

        # 검색창에 맛집 리스트 순서대로 맛집 입력
        print('검색어 입력 중')
        search.send_keys(i)
        time.sleep(2)


        # 검색창으로 검색(엔터를 누름)
        search.send_keys(Keys.ENTER)
        time.sleep(2)

        # 검색창 비우기
        print("검색창을 비우는 중 입니다.")
        search.send_keys(Keys.COMMAND + "a")
        search.send_keys(Keys.BACK_SPACE)
        BROWSER.find_element(By.CLASS_NAME, "btn_clear").click()

        # 맛집을 클릭할 수 있도록 프레임 이동
        print("프레임 이동 중")
        BROWSER.switch_to.frame(BROWSER.find_element(By.ID, 'searchIframe'))
        time.sleep(2)

        # 첫번째로 나온 맛집을 클릭
        print("첫 번째 맛집 클릭")
        good_restaurant = BROWSER.find_element(By.CLASS_NAME, "qbGlu")
        good_restaurant.click()

        # 메인프레임으로 이동
        print("메인 프레임으로 이동 중")
        BROWSER.switch_to.default_content()
        time.sleep(3)

        # 리뷰 페이지로 갈 수 있도록 프레임 이동
        print("프레임 이동 중")
        BROWSER.switch_to.frame(BROWSER.find_element(By.ID, 'entryIframe'))
        time.sleep(2)

        # 리뷰 버튼 클릭
        print("리뷰 버튼 클릭")
        BROWSER.find_elements(By.CLASS_NAME, "veBoZ")[3].click()

        # 블로그 리뷰 버튼 클릭
        print('블로그 리뷰 버튼 클릭')
        btns = BROWSER.find_elements(By.CLASS_NAME, "YsfhA")[1].click()
        for btn in btns:
            if btn.text == "리뷰":
                btn.click()
                break

        # 블로그 url 크롤링
        print("블로그 url를 크롤링 중 입니다.")
        url_data = BROWSER.find_elements(By.CLASS_NAME, "uUMhQ")
        for i in url_data:
            blog_url = i.get_attribute("href")
            BLOG_URL_LIST.append(blog_url)

        # 메인프레임으로 이동
        print("프레임 이동 중")
        BROWSER.switch_to.default_content()

    except:
        break
print(BLOG_URL_LIST)



connection = pymysql.connect(
    host='localhost',
    user='root',
    password='ans!!941105',
    db='naver_crawling',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
# DB 에 데이터를 저장
with connection.cursor() as cur:
    # 만들어 논 list에서 하나씩 블로그에 들어감
    for i in BLOG_URL_LIST:
        try:
            # 블로그에 들어감
            BROWSER.get(i)

            # 스크랩을 할 수 있도록 프레임 전환
            BROWSER.switch_to.frame(BROWSER.find_element(By.ID, 'mainFrame'))

            # 블로그에 타이틀과 리뷰 글을 스크랩
            title = BROWSER.find_element(By.CLASS_NAME, 'pcol1').text
            review = BROWSER.find_element(By.CLASS_NAME, 'se-main-container').text

            # insert를 이용하여 DB에 정보 입력
            sql = "INSERT INTO blog_review (title, review) VALUES (%s, %s)"
            cur.execute(sql, (title, review))
            connection.commit()
            connection.close()

        # 만약 정보가 없거나 예외가 발생시 패스
        except Exception as e:
            print(e)


