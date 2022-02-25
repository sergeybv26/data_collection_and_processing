"""
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем
должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта
(также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
Наименование вакансии.
Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов.
Общий результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.
"""
import re
from pprint import pprint
from threading import Thread

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://hh.ru/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/96.0.4664.174 YaBrowser/22.1.3.848 Yowser/2.5 Safari/537.36'}

vacancy_name = input('Введите наименование искомой вакансии: ')

params = {
    'area': 1,
    'fromSearchLine': 'true',
    'text': vacancy_name,
    'from': 'suggest_post',
    'page': 0,
    'hhtmFrom': 'vacancy_search_list'
}

url = f'{BASE_URL}search/vacancy'

vacancy_dict = {
    'name': [],
    'min_salary': [],
    'max_salary': [],
    'currency': [],
    'vacancy_url': [],
    'site_url': [],
    'company': [],
    'address': []
}
vacancy_list = []


def get_vacancy_from_hh():
    """
    Собирает вакансии с сайта hh.ru
    :return:
    """
    global vacancy_list
    _response = requests.get(url, headers=HEADERS, params=params)
    _dom = BeautifulSoup(response.text, 'html.parser')
    vacancy_list.append(dom.find_all('div', {'class': 'vacancy-serp-item'}))


response = requests.get(url, headers=HEADERS, params=params)
dom = BeautifulSoup(response.text, 'html.parser')
pager = dom.find('div', {'class': 'pager'})
final_page = int(pager.findChildren()[-4].getText())

req_thread_list = []

for page_num in range(final_page + 1):
    params['page'] = page_num
    req_thread_list.append(Thread(target=get_vacancy_from_hh))

for thread in req_thread_list:
    thread.start()

for thread in req_thread_list:
    thread.join()

for vacancy in vacancy_list:
    info = vacancy.find_all(re.compile('vacancy-title'))
    vacancy_dict['name'].append(info.getText())

pprint(vacancy_dict)


# while next_flag:
#     response = requests.get(url, headers=HEADERS, params=params)
#     dom = BeautifulSoup(response.text, 'html.parser')
#
#     vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})
#
#     # paginator = dom.find_all('a', {'data-qa': 'pager-next'})
#
#     # if not paginator:
#     #     next_flag = False
#
#     pager = dom.find('div', {'class': 'pager'})
#     pager_child = pager.findChildren()
#     print(pager_child[-4])
#     break
print()
