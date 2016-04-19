import json, math, scrapy
from collections import defaultdict
from scrape.items import ScrapeItem, ReviewItem

class ScrapeSpider(scrapy.Spider):
    name = "allrecipes"
    allowed_domains = ["allrecipes.com"]
    base_url = "http://allrecipes.com"
    #http://allrecipes.com/recipes/?sort=newest&page=800
    start_urls = [
        "http://allrecipes.com/recipes/76/appetizers-and-snacks/",
        "http://allrecipes.com/recipes/78/breakfast-and-brunch/",
        "http://allrecipes.com/recipes/17561/lunch/",
        "http://allrecipes.com/recipes/17562/dinner/",
        "http://allrecipes.com/recipes/79/desserts/"
    ]
    known_ids = set()
    reviewers = defaultdict(list)
    bad_recipes = []
    bad_reviews = []

    # time: String - e.g. 1 h 25 m
    # output: int - 85
    def get_minutes(self, time):
        acc = 0
        x = time.split('d')
        y = x[0]
        if len(x) > 1:
            acc += int(x[0]) * 1440
            if not x[1] == '':
                y = x[1]
            else:
                return acc
        y = y.split('h')
        z = y[0]
        if len(y) > 1:
            acc += int(y[0]) * 60
            if not y[1] == '':
                z = y[1]
            else:
                return acc
        z = z.split('m')
        acc += int(z[0])
        return acc

    def parse(self, response):
        for i in range(11,51):
            next_page = response.url + "?page=" + str(i) + "&sorttype=popular"
            yield scrapy.Request(next_page, self.get_recipes)

    def get_recipes(self, response):
        all_recipes = response.xpath('.//article[@class="grid-col--fixed-tiles"]')
        for sel in all_recipes:
            recipe_link = sel.xpath('./a[1]/@href').extract()
            recipe_link = recipe_link[0].split('?')[0] if recipe_link else ""
            if not recipe_link == "":
                recipe = ScrapeItem()
                recipe['code'] = recipe_link.split('/')[-3]
                recipe['tag'] = recipe_link.split('/')[-2]
                if not recipe['code'] in self.known_ids:
                    self.known_ids.add(recipe['code'])
                    yield scrapy.Request(self.base_url + recipe_link, self.parse_recipe, meta={'recipe': recipe})

    def parse_recipe(self, response):
        # Log errors
        if response.status >= 400:
            self.logger.warning("Error status at recipe %s", response.url)
            self.bad_recipes.append(response.url)
        recipe = response.meta['recipe']
        name = response.xpath('//h1[@itemprop="name"]/text()').extract()
        recipe['name'] = name[0] if name else ""
        recipe['desc'] = response.xpath('//div[@class="submitter"]/div[@itemprop="description"]/text()').extract_first(default='').replace('\n','').strip()
        # Get time, servings, calories
        header = response.xpath('.//span[@class="recipe-ingredients__header__toggles"]')
        time_raw = header.xpath('./span[@class="ready-in-time__container"]/span[@class="ready-in-time"]/text()').extract_first(default='').replace(' ', '')
        recipe['time'] = self.get_minutes(time_raw) if time_raw else -1
        recipe['servings'] = int(header.xpath('./meta[@itemprop="recipeYield"]/@content').extract_first(default=-1))
        recipe['calories'] = int(header.xpath('.//span[@class="calorie-count"]/span[1]/text()').extract_first(default=-1))
        recipe['ing'] = []
        all_ings = response.xpath('//span[@itemprop="ingredients"]')
        for sel in all_ings:
            temp = sel.xpath('./text()').extract_first(default='')
            if temp:
                recipe['ing'].append(temp)
        # Get instructions
        recipe['steps'] = response.xpath('//ol[@itemprop="recipeInstructions"]/li[@class="step"]/span/text()').extract()
        tips = response.xpath('//section[@class="recipe-footnotes"]/ul[1]/li/text()').extract()
        recipe['tips'] = tips if tips else []
        # Get social
        recipe['rating'] = float(response.xpath('//span[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content').extract_first(default=-1))
        recipe['num_reviews'] = int(response.xpath('//span[@class="recipe-reviews__header--count"]/text()').extract_first(default=-1))
        recipe['reviews'] = []
        base_review_link = "http://allrecipes.com/recipe/getreviews/?recipeid=" + str(recipe['code']) + "&pagenumber=1"
        if recipe['num_reviews'] > 0:
            #for i in range(1, int(math.ceil(recipe['num_reviews']/float(200))) + 1):
            recipe = scrapy.Request(base_review_link + "&pagesize=1000&recipeType=Recipe&sortBy=MostHelpful",
                                    self.parse_reviews,
                                    meta={'recipe':recipe})
        yield recipe

    def parse_reviews(self, response):
        # Log errors
        if response.status >= 400:
            self.logger.warning("Error status at review: %s", response.url)
            self.bad_reviews.append(response.url)
    	recipe = response.meta['recipe']
        # Use this to request the full review text
        read_more_link = "http://allrecipes.com/recipe/"+recipe['code']+"/"+recipe['tag']+"/reviews/"
    	all_reviews = response.xpath('//div[@itemprop="review"]')
        recipe['reviews'] = []
        for sel in all_reviews:
            review = ReviewItem()
            reviewer = sel.xpath('.//div[@class="recipe-details-cook-stats-container"]/a/@href').extract()
            reviewer = reviewer[0].split('/')[-2] if reviewer else ""
            review['reviewer'] = reviewer
            self.reviewers[review['reviewer']].append(recipe['code']) #lol
            rating = sel.xpath('.//div[@class="rating-stars"]/@data-ratingstars').extract()
            review['rating'] = int(rating[0]) if rating else -1
            text = sel.xpath('.//p[@itemprop="reviewBody"]/text()').extract()
            text = text[0] if text else ""
            #if "..." in text:
            #    href = sel.xpath('.//div[@class="review-detail"]/a/@href').extract()
            #    href = href[0].split('/')[-2] if href else ""
            #    if not href == "":
            #        recipe = scrapy.Request(read_more_link + href, self.get_full_review, meta={'review':review, 'recipe':recipe})
            #else:
            review['text'] = text.replace('\n', '').strip()
            recipe['reviews'].append(dict(review))
        return recipe

    def get_full_review(self, response):
        recipe = response.meta['recipe']
        review = response.meta['review']
        review['text'] = response.xpath('//p[@itemprop="reviewBody"]/text()').extract_first(default="").replace('\n','').strip()
        recipe['reviews'].append(review)
        return recipe

#filename = './data/' + response.url.split("/")[-1] + '.html'
#with open(filename, 'wb') as f:
#    f.write(response.body)
