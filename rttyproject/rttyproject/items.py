# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RTinfo(scrapy.Item):
    name = scrapy.Field()
    eval_tex = scrapy.Field()
    eval_point = scrapy.Field()
    visited = scrapy.Field()
    wanna_visit = scrapy.Field()
    MAX_budget_dinner = scrapy.Field()
    MIN_budget_dinner = scrapy.Field()
    MAX_budget_lunch = scrapy.Field()
    MIN_budget_lunch = scrapy.Field()
    seats = scrapy.Field()
    category = scrapy.Field()
    address = scrapy.Field()
    url = scrapy.Field()
    created_at = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()

class RttyprojectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
