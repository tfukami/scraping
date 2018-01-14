# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YPInfo(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    jp_name = scrapy.Field()
    rating = scrapy.Field()
    price = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    address = scrapy.Field()
    review_cnt = scrapy.Field()


class YelpItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
