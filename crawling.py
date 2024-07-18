from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from bs4 import BeautifulSoup
import random


random_sec = random.uniform(2,4)
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)



# 크롤링할 웹페이지
url = "https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage=1&groupId=0"


# 크롬 실행
driver = webdriver.Chrome(options=chrome_options)

# 네이버 플레이스로 접속
driver.get(url)
time.sleep(random_sec)

# 검색창 클릭
elem = driver.find_element(By.NAME, value="sectionBlogQuery")


# 검색에 맛집 입력
elem.send_keys('명동교자')
elem.send_keys(Keys.RETURN)




html = BeautifulSoup(driver.page_source)
html = html.find_all(class_ = "title_post")


print(html)

# 내용을 담을 파일
# data = {"가게이름":"title", "리뷰내용":"review", "리뷰블로그 링크":"link"}
# df = pd.DataFrame(data)
# df.to_csv('맛집리뷰1000선.csv', index=False)



