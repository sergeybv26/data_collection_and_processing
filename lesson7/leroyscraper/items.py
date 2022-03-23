# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, Compose, TakeFirst
from lxml import html
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


def extract_property(item):
    dom = html.fromstring(item)
    item_property = dom.xpath("//dt/text()")[0]
    item_param = ' '.join(dom.xpath("//dd/text()")[0].split())
    return {item_property: item_param}


class LeroyscraperItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(convert_price), output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(correct_photos_link))
    prod_property = scrapy.Field(input_processor=MapCompose(extract_property))
