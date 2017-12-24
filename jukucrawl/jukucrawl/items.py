# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Jukuplace(scrapy.Item):
    name = scrapy.Field()
    date = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    place_name = scrapy.Field()
    address = scrapy.Field()
    grade = scrapy.Field()

class JukucrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
