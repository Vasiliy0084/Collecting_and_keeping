# Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests
import json

artist = 'çher'
my_params = {
    'artist': artist,
    'api_key': '406554f85e6b0658403516ac5aff2b2c'
}
url = "http://ws.audioscrobbler.com/2.0"
response = requests.get(url, method=artist.getinfo, params=my_params, format=json)

print(response.text)



# http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist=Cher&api_key=YOUR_API_KEY&format=json
