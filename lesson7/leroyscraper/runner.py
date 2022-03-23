from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroyscraper import settings
from leroyscraper.spiders.lmru import LmruSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    crawler_process = CrawlerProcess(settings=crawler_settings)
    user_query = input('Введите запрос для поиска: ')
    crawler_process.crawl(LmruSpider, search=user_query)

    crawler_process.start()
