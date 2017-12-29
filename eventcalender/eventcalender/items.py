# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EVinfo(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    start_at = scrapy.Field()
    place = scrapy.Field()

class EventcalenderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
