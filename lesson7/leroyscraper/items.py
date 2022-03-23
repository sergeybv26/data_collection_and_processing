# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, Compose, TakeFirst
from twisted.web.html import output


def correct_photos_link(link):
    link = link.replace('w_82,h_82,', 'w_2000,h_2000,')
    return link


def convert_price(value):
    try:
        value = float(value)
    except ValueError:
        return value
    return value


class LeroyscraperItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(convert_price), output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(correct_photos_link))
