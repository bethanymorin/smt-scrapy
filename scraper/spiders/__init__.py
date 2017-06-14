from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scraper.items import SmtArticleItem, SmtContributorProfileItem
from scraper.utils import (
    get_nodes_to_export_from_db,
    get_author_urls_from_jl,
    write_nodes_to_file,
    get_setting_limits,
    get_out_dir,
)
from scraper.db_settings import execution_path

execution_script_path = execution_path


def update_url_feed(url):
    f = open('urllog.txt', 'ab+')
    f.write(url + '\n')
    f.close()


class SmtStories(CrawlSpider):
    ''' CrawlSpider class for crawling the socialmediatoday.com site

        It should store content from article and author (contributor) profile pages
    '''
    name = "stories"
    limit, offset = get_setting_limits()
    db_nodes = get_nodes_to_export_from_db(0, limit=limit, offset=offset)
    write_nodes_to_file(db_nodes, 'articles')
    allowed_domains = ["socialmediatoday.com"]
    start_urls = ["file://%s/articles.html" % execution_script_path]
    rules = [
        Rule(
            # article page
            # follow links on this page
            LinkExtractor(
                allow=(
                    u'\/[a-zA-Z0-9\-\/]+\/[a-zA-Z0-9\-\/]+$',
                ),
            ),
            callback='parse_article_item',
            follow=False,
        ),
    ]

    # handle an article page here
    def parse_article_item(self, response):
        db_data = self.db_nodes[response.url]
        item = SmtArticleItem()
        item.process(response, db_data)
        update_url_feed(response.url)
        return item


class SmtAuthors(CrawlSpider):
    name = 'authors'
    allowed_domains = ["socialmediatoday.com"]
    out_dir = get_out_dir()
    author_info = get_author_urls_from_jl(source_file='%s/stories.jl' % out_dir)
    write_nodes_to_file(author_info, 'authors')
    start_urls = ["file://%s/authors.html" % execution_script_path]
    rules = [
        Rule(
            # article page
            # follow links on this page
            LinkExtractor(
                allow=(
                    u'\/users\/[a-zA-Z0-9\-\/]+$',
                ),
            ),
            callback='parse_author_item',
            follow=False,
        ),
    ]

    # handle a contributor profile page here
    def parse_author_item(self, response):
        db_data = self.author_info[response.url]
        item = SmtContributorProfileItem()
        item.process(response, db_data)
        update_url_feed(response.url)
        return item