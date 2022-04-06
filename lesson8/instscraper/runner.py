import os

from dotenv import load_dotenv
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from ssh_pymongo import MongoSession

from instscraper import settings
from instscraper.spiders.instcom import InstcomSpider


load_dotenv(dotenv_path='.env')

DB_TYPE = os.getenv('DB_TYPE')
HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')


def query_db(accounts):
    """
    Выполняет запросы к базе и получает данные о подписках и подписчиках пользователей
    :param accounts: Список пользователей
    :return: None
    """
    if DB_TYPE == 'local':
        client = MongoClient('localhost', 27017)
        database = client.instagram
    else:
        client = MongoSession(
            HOST,
            port=22,
            user=USER,
            password=PASSWORD,
            uri='mongodb://127.0.0.1:27017'
        )
        database = client.connection['instagram']

    for account in accounts:
        collection = database[account]
        find_q = collection.find({'follow': 'followers'})
        followers = [item for item in find_q]
        find_q = collection.find({'follow': 'following'})
        following = [item for item in find_q]
        print(f'У пользователя {account} {len(followers)} подписчиков и {len(following)} подписок')


if __name__ == '__main__':

    ACCOUNTS_LIST = ['official_belgorod', 'belgorod.auto']

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstcomSpider, accounts=ACCOUNTS_LIST)

    process.start()

    query_db(ACCOUNTS_LIST)
