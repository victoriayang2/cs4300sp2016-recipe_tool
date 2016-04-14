import scrapy
from scrape.items import ScrapeItem

class ScrapeSpider(scrapy.Spider):
    name = "allrecipes"
    allowed_domains = ["allrecipes.com"]
    base_url = "http://allrecipes.com/recipes"
    start_urls = [
        "http://allrecipes.com/recipes/76/appetizers-and-snacks/",
        "http://allrecipes.com/recipes/78/breakfast-and-brunch/",
        "http://allrecipes.com/recipes/17561/lunch/",
        "http://allrecipes.com/recipes/17562/dinner/",
        "http://allrecipes.com/recipes/79/desserts/"
    ]
    known_ids = set()

    # time: String - e.g. 1 h 25 m
    # output: int - 85
    def get_minutes(time):
        acc = 0
        x = time.replace(' ', '').split('d')
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
        for i in range(1,11):
            next_page = response.url + "?page=" + str(i) + "&sorttype=popular"
            yield scrapy.Request(next_page, self.get_recipes)

    def get_recipes(self, response):
        all_recipes = response.xpath('.//article[@class="grid-col--fixed-tiles"]')
        for sel in all_recipes:
            recipe_link = sel.xpath('./a[1]/@href').extract()[0].split('?')[0]
            recipe = ScrapeItem()
            recipe['id'] = recipe_link.split('/')[-3]
            recipe['tag'] = recipe_link.split('/')[-2]
            if not recipe['id'] in known_ids:
                known_ids.add(recipe['id'])
                yield scrapy.Request(base_url + recipe_link, self.parse_recipe, meta={'recipe': recipe})

    def parse_recipe(self, response):
        recipe = response.meta['recipe']
        recipe['name'] = response.xpath('//h1[@itemprop="name"]/text()').extract()[0]
        recipe['desc'] = response.xpath('//div[@class="submitter"]/div[@itemprop="description"]/text()').extract()[0].replace('\n','').strip()
        # Get time, servings, calories
        header = response.xpath('.//span[@class="recipe-ingredients__header__toggles"]')
        time_raw = header.xpath('./span[@class=ready-in-time]/text()').extract()[0]
        recipe['time'] = get_minutes(time_raw)
        recipe['servings'] = int(header.xpath('./meta[@itemprop="recipeYield"]/@content').extract()[0])
        recipe['calories'] = int(header.xpath('.//span[@class="calorie-count"]/span[1]/text()').extract()[0])
        recipe['ing'] = []
        all_ings = response.xpath('//span[@itemprop="ingredients"]')
        for sel in all_ings:
            recipe['ing'].append(sel.xpath('./text()').extract()[0])
        # Get instructions
        recipe['steps'] = response.xpath('//ol[@itemprop="recipeInstructions"]/li[@class="step"]/span/text()').extract()
        recipe['tips'] = response.xpath('//section[@class="recipe-footnotes"]/ul[1]/li[@class!="recipe-footnotes__header"]/text()').extract()
        # Get social
        recipe['rating'] = float(response.xpath('//span[@class="aggregateRating"]/meta[@itemprop="ratingValue"]/@content').extract()[0])
        recipe['num_made'] = int(response.xpath('//span[@class="made-it-count ng_binding"]/text()').extract()[0])
        recipe['num_reviews'] = int(response.xpath('//span[@class="review-count"]/text()').extract()[0])
        recipe['reviews'] = []
        if recipe['num_reviews'] > 20:
            #take batches of 200
        else:
            #get the 20 shown on the first page
            # all_reviews = response.xpath('//div[@class="reviews-list"]//div[@itemprop="review"]')
            # for sel in all_reviews:
            #     review = {}
            #     review['rating'] = sel.xpath('.//meta[@itemprop="ratingValue"]/@content').extract()[0]
            #     review['author'] = sel.xpath('.//meta[@itemprop="author"]/@content').extract()[0]
            #     review['text'] = sel.xpath('.//div[@class="text-line"]/text()').extract()[0].strip('\n').strip()
            #     recipe['reviews'].append(review)
        yield recipe

    def parse_external(self, response):
    	recipe = response.meta['recipe']
    	source = response.xpath('//iframe/@src').extract()[0]
    	recipe = scrapy.Request(source, callback=self.parse_iframe, meta={'recipe': recipe})
    	return recipe

#filename = './data/' + response.url.split("/")[-1] + '.html'
#with open(filename, 'wb') as f:
#    f.write(response.body)
