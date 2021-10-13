# Написать программу, которая собирает товары «В тренде» с сайта техники mvideo и складывает данные в БД.
# Сайт можно выбрать и свой. Главный критерий выбора: динамически загружаемые товары

import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions as se
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['products']
base = db.products

chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)
url = 'https://www.mvideo.ru/'
driver.get(url)

time.sleep(2)
# Закрываем всплывающее окно, которое не позволяет что-либо делать
driver.find_element(By.CLASS_NAME, "modal-layout__close").click()

# пролистываем сайт вниз до требуемой области
time.sleep(2)

for i in range(2):
    actions = ActionChains(driver)
    actions.key_down(Keys.PAGE_DOWN)
    actions.perform()
    time.sleep(3)

# Нажимаем кнопку "В тренде"
driver.find_element(By.XPATH, "//button[@class='tab-button ng-star-inserted']").click()
time.sleep(2)

# Прокрутка товаров "В тренде"
while True:
    try:
        button = driver.find_elements_by_xpath("//mvid-shelf-group/*//button[@class='btn forward mv-icon-button--primary mv-icon-button--shadow mv-icon-button--medium mv-button mv-icon-button']/mvid-icon[@type='chevron_right']")
        button[1].click()
        time.sleep(2)
    except se.ElementNotInteractableException:
        break

# Собираем данные о товарах

items = driver.find_elements(By.XPATH, "//mvid-shelf-group//mvid-product-cards-group//div[@class='title']")

products = []
for item in items:
    product_list = {}
    name = item.find_element(By.XPATH, "//mvid-shelf-group//mvid-product-cards-group//div[@class='title']").text
    link = item.find_element(By.TAG_NAME, "a").get_attribute('href')
    product_list['name'] = name
    product_list['link'] = link

    products.append(product_list)

# Перенос результатов в базу данных
try:
    base.update_one({'link': product_list['link']}, {'$set': product_list}, upsert=True)
except Exception as exc:
    print('У Вас ошибка/n', exc)

print(products)