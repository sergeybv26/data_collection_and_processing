"""
Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
Сложить собранные новости в БД
"""
from pprint import pprint

import requests
from lxml import html

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/96.0.4664.174 YaBrowser/22.1.3.848 Yowser/2.5 Safari/537.36'}


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

    for item in main_news_items:
        item_dict = {}
        news = item.xpath(".//span[contains(@class, 'photo__title')]/text()")[0].replace('\xa0', ' ')
        news_link = item.xpath(".//a/@href")[0]

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


pprint(get_news_from_mail())
