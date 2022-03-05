"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
которая будет добавлять только новые вакансии/продукты в вашу базу.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше
введённой суммы (необходимо анализировать оба поля зарплаты). Для тех, кто выполнил задание с Росконтролем -
напишите запрос для поиска продуктов с рейтингом не ниже введенного или качеством не ниже введенного
(то есть цифра вводится одна, а запрос проверяет оба поля)
"""
from pprint import pprint
from threading import Thread

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

BASE_URL = 'https://hh.ru/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/96.0.4664.174 YaBrowser/22.1.3.848 Yowser/2.5 Safari/537.36'}

CLIENT_DB = MongoClient('127.0.0.1', 27017)

vacancy_list = []


def get_vacancy_from_hh(_url, _params):
    """
    Собирает вакансии с сайта hh.ru и добавляет в список объекты BeautifulSoup c собранными вакансиями
    :param _url: url, на который выполняется запрос
    :param _params: параметры запроса
    :return: None
    """
    global vacancy_list
    _response = requests.get(_url, headers=HEADERS, params=_params)
    _dom = BeautifulSoup(_response.text, 'html.parser')
    vacancy_list.append(_dom.find_all('div', {'class': 'vacancy-serp-item'}))


def main(vacancy_name, database):
    """
    Главная функция. Собирает вакансии с сайта hh.ru и сохраняет результат в базу данных
    :param vacancy_name: наименование вакансии
    :param database: база данных
    :return: None
    """

    params = {
        'area': 1,
        'fromSearchLine': 'true',
        'text': vacancy_name,
        'from': 'suggest_post',
        'page': 0,
        'hhtmFrom': 'vacancy_search_list'
    }

    url = f'{BASE_URL}search/vacancy'

    response = requests.get(url, headers=HEADERS, params=params)
    dom = BeautifulSoup(response.text, 'html.parser')
    pager = dom.find('div', {'class': 'pager'})
    if pager:
        final_page = int(pager.findChildren()[-4].getText())
    else:
        print('По введенному названию вакансий не найдено')

    req_thread_list = []

    for page_num in range(final_page + 1):
        params['page'] = page_num
        get_vacancy_from_hh(url, params)
        # req_thread_list.append(Thread(target=get_vacancy_from_hh, args=(url, params)))

    # for thread in req_thread_list:
    #     thread.start()
    #
    # for thread in req_thread_list:
    #     thread.join()

    for vacancy in vacancy_list:
        for vacancy_item in vacancy:
            vacancy_dict = {
                '_id': None,
                'name': None,
                'min_salary': None,
                'max_salary': None,
                'currency': None,
                'vacancy_url': None,
                'site_url': None,
                'company': None,
                'address': None
            }
            info = vacancy_item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            vacancy_dict['name'] = info.getText()
            vacancy_dict['vacancy_url'] = f"{info['href']}"
            site_url_list = info['href'].split('/')
            vacancy_dict['site_url'] = f'{site_url_list[0]}//{site_url_list[2]}/'
            vacancy_dict['_id'] = int(site_url_list[4].split('?')[0])
            try:
                salary_str = vacancy_item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText(). \
                    replace('\u202f', '')
                vacancy_dict['company'] = vacancy_item.find('a',
                                                            {'data-qa': 'vacancy-serp__vacancy-employer'}).getText()
                vacancy_dict['address'] = vacancy_item.find('div',
                                                            {'data-qa': 'vacancy-serp__vacancy-address'}).getText()
            except AttributeError:
                pass
            else:
                salary_list = salary_str.split()
                if salary_list[0] == 'от':
                    vacancy_dict['min_salary'] = int(salary_list[1])
                elif salary_list[0] == 'до':
                    vacancy_dict['max_salary'] = int(salary_list[1])
                else:
                    vacancy_dict['min_salary'] = int(salary_list[0])
                    vacancy_dict['max_salary'] = int(salary_list[2])
                vacancy_dict['currency'] = salary_list[-1]

            try:
                database.insert_one(vacancy_dict)
            except DuplicateKeyError:
                pass


def get_vacancy(_salary, database):
    """
    Получает вакансии из базы данных по желаемой минимальной зарплате
    :param _salary: Зарплата
    :param database: база данных
    :return: объект-итератор
    """
    return database.find({'$or': [
        {'min_salary': {'$gt': _salary}},
        {'max_salary': {'$gt': _salary}}
    ]})


if __name__ == '__main__':
    vacancy_name = input('Введите наименование искомой вакансии для заполнения/обновления базы данных: ')

    db = CLIENT_DB[f'hh_{vacancy_name}']
    vacancy_db = db.vacancy
    main(vacancy_name, vacancy_db)

    desired_salary = int(input('Введите желаемую зарплату: '))

    for elem in get_vacancy(desired_salary, vacancy_db):
        pprint(elem)
