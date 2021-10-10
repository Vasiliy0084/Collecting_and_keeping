# Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# Сложить собранные новости в БД
# Минимум один сайт, максимум - все три

from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['db_news']
base = db.news

# Получаем адреса ссылок на новости
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'}
response = requests.get("https://news.mail.ru/")

dom = html.fromstring(response.text)
links = dom.xpath("//li[@class='list__item']//a[@class='list__text']//@href | //a[@class='link link_flex']/@href")

news_links_temp = []
for item in links:
    item = item.split('/')
    news_links_temp.append('/'.join(item[0:5]))

news_inks = news_links_temp
del (news_links_temp)

mail_ru_news = []

# Переходим по ссылкам, получаем запрошенные данные
for item in news_inks:
    news = {}
    request = requests.get(item, headers=headers)
    dom = html.fromstring(request.text)
    name = dom.xpath("//h1/text()")
    source = dom.xpath("//span[@class='note']/a/span[@class='link__text']/text()")
    date = dom.xpath("//span[@class='note__text breadcrumbs__text js-ago']/@datetime")

    news['name'] = name
    news['source'] = source
    news['link'] = item
    news['date'] = date
    mail_ru_news.append(news)

# Перенос результатов в базу данных
try:
    base.update_one({'link': news['link']}, {'$set': news}, upsert=True)
except Exception as exc:
    print('У Вас ошибка/n', exc)


pprint(mail_ru_news)
