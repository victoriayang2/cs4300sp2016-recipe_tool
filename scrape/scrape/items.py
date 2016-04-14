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
    desc = scrapy.Field()
    time = scrapy.Field()
    servings = scrapy.Field()
    calories = scrapy.Field()
    ing = scrapy.Field()
    steps = scrapy.Field()
    tips = scrapy.Field()
    rating = scrapy.Field()
    num_made = scrapy.Field()
    num_reviews = scrapy.Field()
    reviews = scrapy.Field()
