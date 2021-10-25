# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    subscriber_id = scrapy.Field()
    subscriber_name = scrapy.Field()
    subscriber_fullname = scrapy.Field()
    photo = scrapy.Field()
    subscriber_type = scrapy.Field()
