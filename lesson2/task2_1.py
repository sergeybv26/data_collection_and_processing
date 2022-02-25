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
import pandas as pd
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
    for vacancy_item in vacancy:
        info = vacancy_item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        vacancy_dict['name'].append(info.getText())
        vacancy_dict['vacancy_url'].append(f"{info['href']}")
        site_url_list = info['href'].split('/')
        vacancy_dict['site_url'].append(f'{site_url_list[0]}//{site_url_list[2]}/')
        try:
            salary_str = vacancy_item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText().\
                replace('\u202f', '')
        except AttributeError:
            vacancy_dict['min_salary'].append(None)
            vacancy_dict['max_salary'].append(None)
            vacancy_dict['currency'].append(None)
        else:
            salary_list = salary_str.split()
            if salary_list[0] == 'от':
                vacancy_dict['min_salary'].append(int(salary_list[1]))
                vacancy_dict['max_salary'].append(None)
            elif salary_list[0] == 'до':
                vacancy_dict['min_salary'].append(None)
                vacancy_dict['max_salary'].append(int(salary_list[1]))
            else:
                vacancy_dict['min_salary'].append(int(salary_list[0]))
                vacancy_dict['max_salary'].append(int(salary_list[2]))
            vacancy_dict['currency'].append(salary_list[-1])
        vacancy_dict['company'].append(vacancy_item.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).getText())
        vacancy_dict['address'].append(vacancy_item.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).getText())

data_frame = pd.DataFrame(vacancy_dict)
print(data_frame)
data_frame.to_csv('task2_1.csv')
data_frame.to_json('task2_1.json')
