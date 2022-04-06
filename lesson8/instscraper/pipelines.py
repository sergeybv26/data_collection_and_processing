# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

from dotenv import load_dotenv
from itemadapter import ItemAdapter
from pymongo import MongoClient
from ssh_pymongo import MongoSession

load_dotenv(dotenv_path='.env')

DB_TYPE = os.getenv('DB_TYPE')
HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')


class InstscraperPipeline:
    def process_item(self, item, spider):

        return item


class InstDBProcess:
    def __init__(self):
        if DB_TYPE == 'local':
            client = MongoClient('localhost', 27017)
            self.database = client.instagram
        else:
            client = MongoSession(
                HOST,
                port=22,
                user=USER,
                password=PASSWORD,
                uri='mongodb://127.0.0.1:27017'
            )
            self.database = client.connection['instagram']

    def process_item(self, item, spider):
        collection = self.database[item['username']]
        collection.insert_one(item)

        return item

