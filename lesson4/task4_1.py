"""
Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
Сложить собранные новости в БД
"""
import re
from datetime import date
from pprint import pprint

import requests
from lxml import html
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/96.0.4664.174 YaBrowser/22.1.3.848 Yowser/2.5 Safari/537.36'}
CLIENT_DB = MongoClient('127.0.0.1', 27017)
DB = CLIENT_DB['all_main_news']


def get_news_from_mail():
    """
    Собирает новости с сайта mail.ru
    :return: Список словарей
    """
    news_list = []

    response = requests.get('https://news.mail.ru/?_ga=2.121227904.902202898.1646300777-606547558.1617686283',
                            headers=HEADERS)

    dom = html.fromstring(response.text)

    main_news_items = dom.xpath('//div[contains(@class, "daynews__item")]')
    news_items = dom.xpath("//div[@data-logger='news__MainTopNews']//li[@class='list__item']/a")

    for item in main_news_items:
        item_dict = {}
        news = item.xpath(".//span[contains(@class, 'photo__title')]/text()")[0].replace('\xa0', ' ')
        news_link = item.xpath(".//a/@href")[0]

        item_dict['_id'] = news_link.split('/')[-2]
        item_dict['news'] = news
        item_dict['link'] = news_link
        item_dict['source'], item_dict['date'] = get_news_parameters_mail(news_link)

        news_list.append(item_dict)

    for item in news_items:
        item_dict = {}
        news = item.xpath(".//text()")[0].replace('\xa0', ' ')
        news_link = item.xpath(".//@href")[0]
        item_dict['_id'] = news_link.split('/')[-2]
        item_dict['news'] = news
        item_dict['link'] = news_link
        item_dict['source'], item_dict['date'] = get_news_parameters_mail(news_link)

        news_list.append(item_dict)

    return news_list


def get_news_parameters_mail(url):
    """
    Обрабатывает данные сайта mail.ru. Получает данные об источнике новости и дате публикации
    :param url: Ссылка на новость
    :return: кортеж (источник, дата публикации)
    """
    _response = requests.get(url, headers=HEADERS)
    _dom = html.fromstring(_response.text)

    info_element = _dom.xpath("//div[@data-logger='Breadcrumbs']")
    for item in info_element:
        try:
            source = item.xpath(".//span[@class='link__text']/text()")[0]
            news_date = item.xpath(".//span[contains(@class, 'note__text')]/@datetime")[0]
        except IndexError:
            source = ''
            news_date = ''
            print('Не удалось получить параметры новости')

    return source, news_date


def get_news_from_lenta():
    """
    Собирает главные новости с сайта lenta.ru
    :return: список словарей
    """
    news_list = []
    response = requests.get('https://lenta.ru/', headers=HEADERS)

    dom = html.fromstring(response.text)
    news_items = dom.xpath("//div[@class='topnews__column']")

    for item in news_items:
        for elem in item:
            item_dict = {}
            news = elem.xpath(".//span[contains(@class, 'card')]/text()")
            if not news:
                news = elem.xpath(".//h3[contains(@class, 'card')]/text()")[0]
            else:
                news = news[0]
            news_link = elem.xpath(".//a[contains(@class, 'card')]/@href")
            # if not news_link.startswith('http'):
            #     news_link = 'https://lenta.ru' + news_link
            news_date = elem.xpath(".//time[contains(@class, 'card')]/text()")[0]

            # item_dict['_id'] = news_link.split('/')[-2]
            item_dict['news'] = news
            item_dict['link'] = news_link
            item_dict['source'] = 'Lenta.ru'
            item_dict['date'] = str(date.today()) + news_date

            news_list.append(item_dict)

    return news_list


def get_news_from_yandex():
    """
    Собирает новости с сайта yandex.ru
    :return: Список словарей
    """
    news_list = []
    response = requests.get('https://yandex.ru/news/', headers=HEADERS)

    dom = html.fromstring(response.text)

    news_items = dom.xpath("//div[contains(@class, 'mg-grid__item')]")

    for item in news_items:
        item_dict = {}
        if item.xpath(".//div[@class='mg-card__inner']"):
            news = item.xpath(".//div[@class='mg-card__inner']//a[@class='mg-card__link']/text()")[0]
            news_link = item.xpath(".//div[@class='mg-card__inner']//a[@class='mg-card__link']/@href")[0]
        else:
            try:
                news = item.xpath(".//div[@class='mg-card__text-content']//a[@class='mg-card__link']/text()")[0]
                news_link = item.xpath(".//div[@class='mg-card__text-content']//a[@class='mg-card__link']/@href")[0]
            except IndexError:
                continue
        source = item.xpath(".//a[@class='mg-card__source-link']/text()")[0]
        news_date = item.xpath(".//span[@class='mg-card-source__time']/text()")[0]

        item_dict['_id'] = re.findall(r'id=\d*&', news_link)[0][3:]
        item_dict['news'] = news.replace('\xa0', ' ')
        item_dict['link'] = news_link
        item_dict['source'] = source
        item_dict['date'] = news_date

        news_list.append(item_dict)

    return news_list


def save_news(database, data):
    """
    Сохраняет собранные новости в базе данных. Осуществляет проверку на уникальность
    :param database: база данных
    :param data: данные для сохранения в базу - список словарей
    :return: Список элементов, которые не удалось добавить в базу
    """
    error_list = []
    for el in data:
        try:
            database.insert_one(el)
        except DuplicateKeyError:
            error_list.append(el)

    return error_list


def main():
    """
    Основная функция осуществляет запуск сбора и сохранения информации
    :return: None
    """
    news_mail_db = DB.news_mail
    news_mail = get_news_from_mail()
    error_list_mail = save_news(news_mail_db, news_mail)

    pprint(news_mail)
    print('Дубликаты данных mail.ru:')
    pprint(error_list_mail)

    news_lenta_db = DB.news_lenta
    # news_lenta = get_news_from_lenta()
    # error_list_mail = save_news(news_lenta_db, news_lenta)

    # pprint(news_lenta)
    # print('Дубликаты данных lenta.ru:')
    # pprint(error_list_mail)

    news_ya_db = DB.news_ya
    news_ya = get_news_from_yandex()
    error_list_ya = save_news(news_ya_db, news_ya)

    pprint(news_ya)
    print('Дубликаты данных yandex.ru:')
    pprint(error_list_ya)


if __name__ == '__main__':
    main()
