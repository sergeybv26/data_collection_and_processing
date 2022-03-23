import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from leroyscraper.items import LeroyscraperItem


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f"https://leroymerlin.ru/search/?q={kwargs.get('search')}"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']/href")
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@data-qa='product-name']")
        for link in links:
            yield response.follow(link, callback=self.parse_prod)

    def parse_prod(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyscraperItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//uc-pdp-price-view/meta[@itemprop='price']/@content")
        loader.add_xpath('photos', "//img[@slot='thumbs']/@src")
        yield loader.load_item()
