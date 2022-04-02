# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VacancyscraperItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    salary_cur = scrapy.Field()
    url = scrapy.Field()
