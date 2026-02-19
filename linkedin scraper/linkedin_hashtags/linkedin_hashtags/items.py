# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags


class HashtagItem(scrapy.Item):
    """Item for storing LinkedIn hashtag data"""
    name = scrapy.Field()
    original_case = scrapy.Field()
    url = scrapy.Field()
    mentions = scrapy.Field()
    context = scrapy.Field()
    sentiment_score = scrapy.Field()
    sentiment_polarity = scrapy.Field()
    scraped_at = scrapy.Field()
    post_text = scrapy.Field()
    author = scrapy.Field()
