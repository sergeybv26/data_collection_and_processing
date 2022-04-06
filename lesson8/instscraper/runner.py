from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instscraper import settings
from instscraper.spiders.instcom import InstcomSpider

if __name__ == '__main__':

    ACCOUNTS_LIST = ['official_belgorod', 'belgorod.auto']

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstcomSpider, accounts=ACCOUNTS_LIST)

    process.start()
