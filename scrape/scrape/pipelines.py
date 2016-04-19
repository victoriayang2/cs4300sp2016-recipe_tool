# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

class ScrapePipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWriterPipeline(object):

    def __init__(self):
        self.file = open("/Volumes/Macintosh HD/Users/danieldouvris/Documents/recipes/allrecipes.json", 'ab')

    # This method is called when the spider returns an item
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

    # This method is called when the spider is closed.
    def close_spider(self, spider):
    	reviewers = open("/Volumes/Macintosh HD/Users/danieldouvris/Documents/recipes/reviewers.json", 'ab')
    	reviewers.write(json.dumps(spider.reviewers))
    	reviewers.close()
    	self.file.close()
        if len(spider.bad_recipes) > 0:
            failed_urls = open("/Volumes/Macintosh HD/Users/danieldouvris/Documents/recipes/retry_recipes.txt", 'ab')
            for url in spider.bad_recipes:
                failed_urls.write(url + "\n")
            failed_urls.close()
        if len(spider.bad_reviews) > 0:
            failed_urls = open("/Volumes/Macintosh HD/Users/danieldouvris/Documents/recipes/retry_reviews.txt", 'ab')
            for url in spider.bad_reviews:
                failed_urls.write(url + "\n")
            failed_urls.close()