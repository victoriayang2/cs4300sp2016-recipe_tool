# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    ing = scrapy.Field()
    time = scrapy.Field()
    time_unit = scrapy.Field()
    steps = scrapy.Field()
    nutrition = scrapy.Field()
    tastes = scrapy.Field()
    tags = scrapy.Field()
    rating = scrapy.Field()
    num_reviews = scrapy.Field()
    reviews = scrapy.Field()
