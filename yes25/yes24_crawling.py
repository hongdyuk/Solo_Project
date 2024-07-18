from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pymysql
import time
import re
from datetime import datetime

# ChromeDriverManager().install()

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)


# 크롬 드라이버 실행
browser = webdriver.Chrome()

# 예스24 베스트 3 페이지의 모든 책 링크를 list 안에 담는다. 
link_list = []
for i in range(1,4):
    print(f'현재 {i} 페이지를 수집 중 입니다!')
    url = f'https://www.yes24.com/Product/Category/BestSeller?categoryNumber=001&pageNumber={i}&pageSize=24'
    browser.get(url)

    datas = browser.find_elements(By.CLASS_NAME, 'gd_name')
    for i in datas:
        link = i.get_attribute('href')
        link_list.append(link)

    time.sleep(1)

# DB와 python을 연결 시킨다
conn = pymysql.connect(
    host = 'localhost',
    user = 'root',
    password = 'ans!!941105',
    db = 'yes24',
    charset = 'utf8mb4',
    cursorclass = pymysql.cursors.DictCursor
)

# DB TABLE 안에 크롤링한 데이터를 INSERT 한다. 
with conn.cursor() as cur:
    for i in link_list:
        try:
            browser.get(i)

            title = browser.find_element(By.CLASS_NAME, 'gd_name').text
            author = browser.find_element(By.CLASS_NAME, 'gd_auth').text
            publisher = browser.find_element(By.CLASS_NAME, 'gd_pub').text
            publishing = browser.find_element(By.CLASS_NAME, 'gd_date').text

            match = re.search(r'(\d+)년 (\d+)월 (\d+)일', publishing)
            if match:
                year, month, day = match.groups()
                data_obj = datetime(int(year), int(month), int(day))
                publishing = data_obj.strftime("%Y-%m-%d")
            else:
                publishing = "2024-07-18"

            rating = browser.find_element(By.CLASS_NAME, 'yes_b').text

            review = browser.find_element(By.CLASS_NAME, 'txC_blue').text
            try:
                review = int(review.replace(",",""))
            except:
                pass

            sales = browser.find_element(By.CLASS_NAME, 'gd_sellNum').text.split(' ')[2]
            sales = int(sales.replace(",",""))

            price = browser.find_element(By.CLASS_NAME, 'yes_m').text[:-1]
            price = int(price.replace(",",""))

            try:
                full_text = browser.find_element(By.CLASS_NAME, 'gd_best').text
                parts = full_text.split(" | ")
                ranking_part = parts[0]
                ranking = ''.join(filter(str.isdigit, ranking_part)) #숫자만 추출
            except:
                ranking = 0

            try:
                full_text = browser.find_element(By.CLASS_NAME, 'gd_best').text
                parts = full_text.split(" | ")
                ranking_weeks_part = parts[1]
                ranking_weeks = ''.join(filter(str.isdigit, ranking_weeks_part.split()[-1]))
            except:
                ranking_weeks = 0

            sql = """INSERT INTO Books(
                title, author, publisher, publishing, rating, sales, price, ranking, ranking_weeks
                )
                VALUES(
                %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
            time.sleep(1)
            cur.execute(sql, (title, author, publisher, publishing, rating, sales, price, ranking, ranking_weeks))
            conn.commit()

        except Exception  as e:
            print(e)