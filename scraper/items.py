# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SmtArticleItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    page_title = scrapy.Field()
    body = scrapy.Field()
    pub_date = scrapy.Field()
    topic = scrapy.Field()
    author_profile_link = scrapy.Field()
    byline = scrapy.Field()


class SmtContributorProfileItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    page_title = scrapy.Field()
    body = scrapy.Field()
