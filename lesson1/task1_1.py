"""
1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для
конкретного пользователя, сохранить JSON-вывод в файле *.json.
"""
import json
from pprint import pprint

import requests

USERNAME = 'sergeybv26'

response = requests.get(f'https://api.github.com/users/{USERNAME}/repos')

resp_json = response.json()

pprint(resp_json)

with open('task1_1.json', 'w', encoding='utf-8') as res_file:
    json.dump(resp_json, res_file)
