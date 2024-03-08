# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SteamItem(scrapy.Item):
    link = scrapy.Field()
    platforms = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    categories = scrapy.Field()
    rev_number = scrapy.Field()
    overall_score = scrapy.Field()
    rel_date = scrapy.Field()
    developer = scrapy.Field()
    tags = scrapy.Field()
