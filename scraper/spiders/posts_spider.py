import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scraper.items import SmtArticleItem, SmtContributorProfileItem


class Smt(scrapy.Spider):
    name = "smt"

    allowed_domains = ["socialmediatoday.com"]
    start_urls = ['http://socialmediatoday.com/']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scraper.pipelines.SmtArticlePipeline': 300,
            'scraper.pipelines.SmtContributorPipeline': 300,
        },
    }

    rules = [
        Rule(
            # article page
            LinkExtractor(
                allow=(u'socialmediatoday.com/marketing/([^/]+)/(\d+)/'),
            ),
            callback='parse_article_item',
            follow=True
        ),
        Rule(
            # contributor profile page
            LinkExtractor(
                allow=(u'socialmediatoday.com/users/([^/]+)/(\d+)/'),
            ),
            callback='parse_contributor_item',
            follow=True
        ),
    ]

    def parse(self, response):
        pass

    def parse_article_item(self, response):
        item = SmtArticleItem()
        import pdb
        pdb.set_trace()
        return item

    def parse_contributor_item(self, response):
        item = SmtContributorProfileItem()
        import pdb
        pdb.set_trace()
        return item
