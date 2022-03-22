# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

from dotenv import load_dotenv
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from ssh_pymongo import MongoSession

load_dotenv(dotenv_path='.env')

DB_TYPE = os.getenv('DB_TYPE')
HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')

if DB_TYPE == 'local':
    CLIENT = MongoClient('localhost', 27017)
    DATABASE = CLIENT.vacancy
else:
    CLIENT = MongoSession(
        HOST,
        port=22,
        user=USER,
        password=PASSWORD,
        uri='mongodb://127.0.0.1:27017'
    )
    DATABASE = CLIENT.connection['vacancy']


class VacancyscraperPipeline:
    def __init__(self):
        self.database = DATABASE

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            site_url_list = item['url'].split('/')
            item['_id'] = int(site_url_list[4].split('?')[0])
            if item['salary'][0] == 'от ' and item['salary'][2] != ' до ':
                item['salary_min'] = int(item['salary'][1].replace('\xa0', ''))
                item['salary_max'] = None
                item['salary_cur'] = item['salary'][-2]
            elif item['salary'][0] == 'до ':
                item['salary_max'] = int(item['salary'][1].replace('\xa0', ''))
                item['salary_min'] = None
                item['salary_cur'] = item['salary'][-2]
            elif item['salary'][0] == 'от ' and item['salary'][2] == ' до ':
                item['salary_min'] = int(item['salary'][1].replace('\xa0', ''))
                item['salary_max'] = int(item['salary'][3].replace('\xa0', ''))
                item['salary_cur'] = item['salary'][-2]
            else:
                item['salary_min'] = None
                item['salary_max'] = None
                item['salary_cur'] = None
            del item['salary']
        else:
            item['_id'] = item['url'].split('-')[-1].split('.')[0]
            if item['salary'][0] == 'от':
                salary_list = item['salary'][2].split('\xa0')
                salary_min = salary_list[0] + salary_list[1]
                item['salary_min'] = int(salary_min)
                item['salary_max'] = None
                item['salary_cur'] = salary_list[-1]
            elif item['salary'][0] == 'до':
                salary_list = item['salary'][2].split('\xa0')
                salary_max = salary_list[0] + salary_list[1]
                item['salary_max'] = int(salary_max)
                item['salary_min'] = None
                item['salary_cur'] = salary_list[-1]
            elif item['salary'][0][0].isdigit():
                item['salary_min'] = int(item['salary'][0].replace('\xa0', ''))
                item['salary_max'] = int(item['salary'][4].replace('\xa0', ''))
                item['salary_cur'] = item['salary'][-3]
            else:
                item['salary_min'] = None
                item['salary_max'] = None
                item['salary_cur'] = None
            del item['salary']

        collection = self.database[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            print('DUP!!!')
        return item
