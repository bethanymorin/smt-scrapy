# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SmtContributorProfileItem(scrapy.Item):
    """ Represents the content of a Contributor Profile page as a scrapy Item object
    """
    page_type = scrapy.Field()
    uid = scrapy.Field()
    email = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    page_title = scrapy.Field()
    fullname = scrapy.Field()
    company_name = scrapy.Field()
    job_title = scrapy.Field()
    headshot_url = scrapy.Field()
    website = scrapy.Field()
    facebook_url = scrapy.Field()
    twitter_url = scrapy.Field()
    linkedin_url = scrapy.Field()
    google_url = scrapy.Field()
    bio = scrapy.Field()


class SmtArticleItem(scrapy.Item):
    """ Represents the content of an Article page as a scrapy Item object
    """
    page_type = scrapy.Field()
    node_id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    canonical_url = scrapy.Field()
    meta_description = scrapy.Field()
    story_title = scrapy.Field()
    body = scrapy.Field()
    pub_date = scrapy.Field()
    byline = scrapy.Field()
    changed = scrapy.Field()
    contributor_profile_url = scrapy.Field()
    contributor_email = scrapy.Field()
    contributor_uid = scrapy.Field()
    legacy_content_type = scrapy.Field()
