# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SmtArticleItem(scrapy.Item):
    """
    Represents the content of an Article page as a scrapy Item object.
    """
    page_type = scrapy.Field()
    url = scrapy.Field()
    url_path = scrapy.Field()
    node_id = scrapy.Field()
    contributor_uid = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    canonical_url = scrapy.Field()
    pub_date = scrapy.Field()
    byline = scrapy.Field()
    body = scrapy.Field()


class SmtContributorProfileItem(scrapy.Item):
    """
    Represents the content of a Contributor Profile page as a scrapy Item
    object.
    """
    page_type = scrapy.Field()
    uid = scrapy.Field()
    url = scrapy.Field()
    url_path = scrapy.Field()
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    company_name = scrapy.Field()
    job_title = scrapy.Field()
    headshot_url = scrapy.Field()
    website = scrapy.Field()
    bio = scrapy.Field()
    facebook = scrapy.Field()
    linkedin = scrapy.Field()
    google = scrapy.Field()
    twitter_handle = scrapy.Field()
