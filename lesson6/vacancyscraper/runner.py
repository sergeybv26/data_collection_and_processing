from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from vacancyscraper import settings
from vacancyscraper.spiders.hhru import HhruSpider
from vacancyscraper.spiders.sjru import SjruSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HhruSpider)
    crawler_process.crawl(SjruSpider)

    crawler_process.start()
