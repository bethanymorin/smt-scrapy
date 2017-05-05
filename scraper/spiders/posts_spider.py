from scrapy.spiders import CrawlSpider
from scraper.items import SmtArticleItem, SmtContributorProfileItem
from scraper.utils import get_nodes_to_export_from_db, get_author_urls_from_jl


class SmtStories(CrawlSpider):
    ''' CrawlSpider class for crawling the socialmediatoday.com site

        It should store content from article and author (contributor) profile pages
    '''
    name = "stories"

    db_nodes = get_nodes_to_export_from_db(0, limit=1000)
    allowed_domains = ["socialmediatoday.com"]
    start_urls = db_nodes.keys()

    # handle an article page here
    def parse(self, response):
        db_data = self.db_nodes[response.url]
        item = SmtArticleItem()
        item.process(response, db_data)
        return item


class SmtAuthors(CrawlSpider):
    name = 'authors'
    allowed_domains = ["socialmediatoday.com"]
    author_info = get_author_urls_from_jl()
    start_urls = author_info.keys()

    # handle a contributor profile page here
    def parse(self, response):
        db_data = self.author_info[response.url]
        item = SmtContributorProfileItem()
        item.process(response, db_data)
        return item
