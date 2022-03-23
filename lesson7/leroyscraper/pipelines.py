# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

import scrapy
from dotenv import load_dotenv
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from scrapy.pipelines.images import ImagesPipeline
from ssh_pymongo import MongoSession

load_dotenv(dotenv_path='.env')

DB_TYPE = os.getenv('DB_TYPE')
HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')


class LeroyscraperPipeline:
    def process_item(self, item, spider):
        item['_id'] = item['url'].split('/')[-2].split('-')[-1]
        print()
        return item


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as err:
                    print(err)

    def item_completed(self, results, item, info):
        item['photos'] = [elem[1] for elem in results if elem[0]]
        return item


class LeroyDBProcess:
    def __init__(self):
        if DB_TYPE == 'local':
            client = MongoClient('localhost', 27017)
            self.database = client.leroyprod
        else:
            client = MongoSession(
                HOST,
                port=22,
                user=USER,
                password=PASSWORD,
                uri='mongodb://127.0.0.1:27017'
            )
            self.database = client.connection['leroyprod']

    def process_item(self, item, spider):
        collection = self.database[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            print('DUP!!!')
        return item
