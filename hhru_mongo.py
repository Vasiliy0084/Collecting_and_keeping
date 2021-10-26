# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию. Добавить в решение со сбором вакансий(продуктов) функцию,
# которая будет добавлять только новые вакансии/продукты в вашу базу.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты - минимальнную и максимульную). Для тех, кто выполнил задание с Росконтролем - напишите запрос для поиска
# продуктов с рейтингом не ниже введенного или качеством не ниже введенного (то есть цифра вводится одна, а запрос проверяет оба поля)


import re
import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pprint import pprint

# Проверяем есть ли уже такая запись в базе
def check(s):
    for doc in base.find({'link': s}):
        return True

# Создаем базу данных
client = MongoClient('127.0.0.1', 27017)
db = client['hh_vacancies']
base = db.hh_vacancies



# Осуществляем поиск вакансий
url = 'https://hh.ru'
search_vacancy = input('Введите название вакансии: ')

params = {'L_save_area': 'true',
    'clusters': 'true',
    'enable_snippets': 'true',
    'text': search_vacancy,
    'area': 113
    }

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
vacancy_number = 1
page = 0
vacancies = []
while True:
    response = requests.get(url + '/search/vacancy/', params=params, headers=headers)
    soup = bs(response.text, 'html.parser')

    vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

    button_next = soup.find('a', text='дальше')



    for vacancy in vacancy_list:
        vacancy_data = {}
        vacancy_info = vacancy.find('a', attrs={'class': 'bloko-link'})
        vacancy_name = vacancy_info.text
        vacancy_link = vacancy_info['href']
        vacancy_employer = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        if not vacancy_employer:
            vacancy_employer = None
        else:
            vacancy_employer = vacancy_employer.text
        vacancy_location = vacancy.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
        vacancy_salary = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if not vacancy_salary:
            vacancy_salary_min = None
            vacancy_salary_max = None
            vacancy_salary_currency = None
        else:
            vacancy_salary = vacancy_salary.getText() \
                .replace(u'\u202f', u'')

            vacancy_salary = re.split(r'\s|-', vacancy_salary)

            if vacancy_salary[0] == 'до':
                vacancy_salary_min = None
                vacancy_salary_max = int(vacancy_salary[1])
            elif vacancy_salary[0] == 'от':
                vacancy_salary_min = int(vacancy_salary[1])
                vacancy_salary_max = None
            else:
                vacancy_salary_min = int(vacancy_salary[0])
                vacancy_salary_max = int(vacancy_salary[2])

            vacancy_salary_currency = vacancy_salary[-1]

        vacancy_data['vacancy_number'] = vacancy_number
        vacancy_data['name'] = vacancy_name
        vacancy_data['link'] = vacancy_link
        vacancy_data['employer'] = vacancy_employer
        vacancy_data['location'] = vacancy_location
        vacancy_data['salary_min'] = vacancy_salary_min
        vacancy_data['salary_max'] = vacancy_salary_max
        vacancy_data['salary_currency'] = vacancy_salary_currency
        vacancy_data['site'] = url

        vacancy_number = vacancy_number + 1

# Проверяем есть ли запись эта ваансия в базе данных и если нет, добавляем
        if check(vacancy_data['link']) is True:
            continue
        else:
            base.insert_one(vacancy_data)

# Проверяем наличие кнопки "Дальше"
    if not button_next or not response.ok:
        break

    page += 1
    params = {'L_save_area': 'true',
              'clusters': 'true',
              'enable_snippets': 'true',
              'text': search_vacancy,
              'area': 113,
              'page': page}


# Проверяем уровень зарплаты

salary_level = int(input('Введите уровень зарплаты: '))

for doc in base.find({'$or': [{'salary_min': {'$gte': salary_level}},
                                {'salary_max': {'$gte': salary_level}}
                                  ]
                          }
                         ):
    pprint(doc)