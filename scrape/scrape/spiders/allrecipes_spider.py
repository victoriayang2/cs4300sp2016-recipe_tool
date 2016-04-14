import scrapy
from scrape.items import ScrapeItem

class ScrapeSpider(scrapy.Spider):
    name = "allrecipes"
    allowed_domains = ["allrecipes.com"]
    start_urls = [
        "http://allrecipes.com/recipes/78/breakfast-and-brunch/?page=1&sorttype=popular",
        "http://allrecipes.com/recipes/76/appetizers-and-snacks/?page=1&sorttype=popular",
        "http://allrecipes.com/recipes/17561/lunch/?page=1&sorttype=popular",
        "http://allrecipes.com/recipes/17562/dinner/?page=1&sorttype=popular",
        "http://allrecipes.com/recipes/79/desserts/?page=1&sorttype=popular"
    ]

    def parse(self, response):
        print response.url

    def parse_recipe(self, response):
        recipe = ScrapeItem()
        recipe['name'] = response.xpath('//*[@itemprop="name"]/text()').extract()[0]
        recipe['time'] = response.xpath('//ul[@class="recipe-data"]/li[@class="time-data"]/span[@class="bd"]/text()').extract()
        recipe['time_unit'] = response.xpath('//ul[@class="recipe-data"]/li[@class="time-data"]/span[@class="ft"]/text()').extract()
        recipe['ing'] = []
        all_ings = response.xpath('//*[@itemprop="ingredients"]')
        for sel in all_ings:
            ing = {}
            amount_span = sel.xpath('.//span[@class="amount"]')
            children = amount_span.xpath('.//span[@class="fraction"]')
            if len(children) == 0:
                ing['amount'] = amount_span.xpath('./text()').extract()
            else:   #get the fraction
                num = float(children.xpath('.//span[@class="numerator"]/text()').extract()[0])
                denom = float(children.xpath('.//span[@class="denominator"]/text()').extract()[0])
                unit = amount_span.xpath('./text()').extract()
                ing['amount'] = '' + str(num/denom) + unit
            ing['name'] = sel.xpath('.//strong[@class="name"]/text()').extract()
            recipe['ing'].append(ing)
        footer = response.xpath('//div[@id="recipe-nutrition"]/div')
        # Get nutrition
        nutrition_sel = footer.xpath('./div[@class="nutrition"]')
        nt = {}
        if len(nutrition_sel) > 0:
            nt['servings'] = nutrition_sel.xpath('.//p[@itemprop="recipeYield"]/text()').extract()[0]
            nt['calories'] = int(nutrition_sel.xpath('.//span[@itemprop="calories"]/text()').extract()[0])
            nt['fat'] = int(nutrition_sel.xpath('.//span[@itemprop="fatContent"]/text()').extract()[0].strip())
            nt['transfat']
        # Get tastes
        taste_sel = footer.xpath('./div[@class="taste"]')
        tastes = []
        if len(taste_sel) > 0:
            all_tastes = taste_sel.xpath('./div')
            for sel in all_tastes:
                t = sel.xpath('.//h5/text()').extract()
                v = sel.xpath('.//div[@class="ninja-level"]/@width').extract()
                tastes.append({'name':t, 'value':v})
        recipe['tastes'] = tastes
        # Get tags
        tag_sel = footer.xpath('./div[@class="recipe-tags"]')
        tags = []
        if len(tag_sel) > 0:
            all_tags = tag_sel.xpath('./div/a/text()').extract()
            tags = all_tags
        recipe['tags'] = tags
        # Get social
        recipe['rating'] = response.xpath('//span[@itemprop="aggregateRating"]//meta[@itemprop="ratingValue"]/@content').extract()[0]
        recipe['num_reviews'] = response.xpath('//span[@itemprop="aggregateRating"]//meta[@itemprop="reviewCount"]/@content').extract()[0]
        recipe['reviews'] = []
        all_reviews = response.xpath('//div[@class="reviews-list"]//div[@itemprop="review"]')
        for sel in all_reviews:
            review = {}
            review['rating'] = sel.xpath('.//meta[@itemprop="ratingValue"]/@content').extract()[0]
            review['author'] = sel.xpath('.//meta[@itemprop="author"]/@content').extract()[0]
            review['text'] = sel.xpath('.//div[@class="text-line"]/text()').extract()[0].strip('\n').strip()
            recipe['reviews'].append(review)
        # Check if instructions are external
        external = response.xpath('//div[@class="external-directions flex-box"]')
        if len(external) > 0:
            # Request external instructions
            external_recipe = response.xpath('./a[@id="source-full-directions"]/@href').extract()
            url = response.urljoin(external_recipe[0])
            recipe = scrapy.Request(url, callback=self.parse_external, meta={'recipe': recipe})
        else:
            # Get local instructions
            recipe['steps'] = response.xpath('//ol[@itemprop="recipeInstructions"]/li[@class="prep-step"]/text()')
        yield recipe

    def parse_iframe(self, response):
   		recipe = response.meta['recipe']
   		steps = response.xpath('//*[@itemprop="recipeInstructions"]/text()').extract()
   		recipe['steps'] = steps
   		return recipe

    def parse_external(self, response):
    	recipe = response.meta['recipe']
    	source = response.xpath('//iframe/@src').extract()[0]
    	recipe = scrapy.Request(source, callback=self.parse_iframe, meta={'recipe': recipe})
    	return recipe

#filename = './data/' + response.url.split("/")[-1] + '.html'
#with open(filename, 'wb') as f:
#    f.write(response.body)
