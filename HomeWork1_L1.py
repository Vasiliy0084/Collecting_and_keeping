# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

# Ссылка на документацию: https://docs.github.com/en/rest/reference/repos#list-repositories-for-a-user

import requests
from pprint import pprint
import json

url = 'https://api.github.com'
user = 'Vasiliy0084'


result = requests.get(f'{url}/users/{user}/repos')


with open('list.json', 'w') as list:
    json.dump(result.json(), list)

for i in result.json():
    pprint(i['name'])