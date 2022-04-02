import scrapy
from scrapy.http import HtmlResponse

from vacancyscraper.items import VacancyscraperItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[contains(@class, 'f-test-vacancy-item')]//a[@target='_blank']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name_value = response.css('h1::text').get()
        salary_value = response.xpath("//div[contains(@class, 'f-test-vacancy-base-info')]/"
                                      "div[2]/div/div/div/span//text()").getall()
        url_value = response.url
        yield VacancyscraperItem(name=name_value, salary=salary_value, url=url_value)
