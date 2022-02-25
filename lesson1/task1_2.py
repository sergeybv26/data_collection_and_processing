"""
2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию.
Ответ сервера записать в файл.
Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide).
Сделайте запрос, чтобы получить список всех сообществ на которые вы подписаны.
"""
import json
from pprint import pprint

import requests

"""
Получение информации о музыкальных исполнителях
"""

API_KEY = '8d346856d7649c69dfb108ed85f1cb96'
API_ROOT = 'http://ws.audioscrobbler.com/2.0/'
ARTIST = 'The Cranberries'

response = requests.get(f'{API_ROOT}?method=artist.getinfo&artist={ARTIST}&api_key={API_KEY}&format=json')

result = response.json()

pprint(result)

with open('task1_2.json', 'w', encoding='utf-8') as res_file:
    json.dump(result, res_file)
