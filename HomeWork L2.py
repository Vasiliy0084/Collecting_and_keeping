# Вариант 1
# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем должность) с сайтов HH(обязательно)
# и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
# Наименование вакансии.
# Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть одинаковая для вакансий с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.

# https://hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&text=data+analyst&showClusters=true

import requests
from bs4 import BeautifulSoup as bs
import re
import json

url = 'https://hh.ru'
search_vacancy = input('Введите название вакансии: ')

params = {'L_save_area': 'true',
    'clusters': 'true',
    'enable_snippets': 'true',
    'text': search_vacancy,
    'showClusters': 'true'}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
page = 0

while True:
    response = requests.get(url + '/search/vacancy/', params=params, headers=headers)
    soup = bs(response.text, 'html.parser')

    vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

    button_next = soup.find('a', text='дальше')

    vacancies = []
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
        vacancy_location = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
        vacancy_salary = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if not vacancy_salary:
            vacancy_salary_min = None
            vacancy_salary_max = None
            vacancy_salary_currency = None
        else:
            vacancy_salary = vacancy_salary.getText() \
                .replace(u'\xa0', u'')

            vacancy_salary = re.split(r'\s|-', vacancy_salary)

            if vacancy_salary[0] == 'до':
                vacancy_salary_min = None
                vacancy_salary_max = int(vacancy_salary[1])
            elif vacancy_salary[0] == 'от':
                vacancy_salary_min = int(vacancy_salary[1])
                vacancy_salary_max = None
            else:
                vacancy_salary_min = int(vacancy_salary[0])
                vacancy_salary_max = int(vacancy_salary[1])

            vacancy_salary_currency = vacancy_salary[2]

        vacancy_data['name'] = vacancy_name
        vacancy_data['link'] = vacancy_link
        vacancy_data['employer'] = vacancy_employer
        vacancy_data['location'] = vacancy_location
        vacancy_data['salary_min'] = vacancy_salary_min
        vacancy_data['salary_max'] = vacancy_salary_max
        vacancy_data['salary_currency'] = vacancy_salary_currency
        vacancy_data['site'] = url

        vacancies.append(vacancy_data)
    if not button_next or not response.ok:
        break

    page += 1
    params = {'L_save_area': 'true',
              'clusters': 'true',
              'enable_snippets': 'true',
              'text': search_vacancy,
              'showClusters': 'true',
              'page': page}

with open('vacancies.json', 'w') as json_file:
    json.dump(vacancies, json_file)
