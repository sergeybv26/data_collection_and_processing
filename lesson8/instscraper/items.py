# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstscraperItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    f_user_id = scrapy.Field()
    f_username = scrapy.Field()
    f_full_name = scrapy.Field()
    f_photo = scrapy.Field()
    follow = scrapy.Field()
