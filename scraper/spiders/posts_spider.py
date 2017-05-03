from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scraper.items import SmtArticleItem, SmtContributorProfileItem


class Smt(CrawlSpider):
    ''' CrawlSpider class for crawling the socialmediatoday.com site

        It should store content from article and author (contributor) profile pages
    '''

    name = "smt"

    allowed_domains = ["socialmediatoday.com"]
    start_urls = [
        'http://www.socialmediatoday.com/',
    ]

    # these are the top level links that we want to follow
    # they also happen to typcially be included in the URL for an article page,
    # which typically looks like
    #   http://www.socialmediatoday.com/social-networks/twitter-launches-new-original-live-programming-lineup
    topics_string = 'marketing|social-networks|technology-data|social-business'

    rules = [
        Rule(
            # topic and tag pages - send them to a do-nothing function just for tracking
            # but follow links on these pages
            LinkExtractor(
                allow=(
                    u'\/categories\/(%s)+\?*' % topics_string,
                    u'\/tags\/[a-zA-Z0-9\-\/]+'
                ),
            ),
            callback='parse_category_page',
            follow=True,
        ),
        Rule(
            # article page
            # follow links on this page
            LinkExtractor(
                allow=(
                    u'\/(%s)+\/[a-zA-Z0-9\-\/]+$' % topics_string,
                ),
            ),
            callback='parse_article_item',
            follow=True,
        ),
        Rule(
            # contributor profile page
            # only follow these links when they are in the by line area of an article
            # follow links because the profile will have article links under
            # "most recent posts"
            LinkExtractor(
                allow=(u'/users/'),
                restrict_css=('div.field-name-post-date-author-name'),
            ),
            callback='parse_contributor_item',
            follow=True
        ),
    ]

    # we don't store anything from these pages
    # but I am curious about when we hit them
    def parse_category_page(self, response):
        if '/tags/' in response.url:
            print "HEY! tags list page: %s" % response.url
        else:
            print "HEY! category list page: %s" % response.url

    # handle an article page here
    def parse_article_item(self, response):
        item = SmtArticleItem()
        item.process(response)
        return item

    # handle a contributor profile page here
    def parse_contributor_item(self, response):
        item = SmtContributorProfileItem()
        item.process(response)
        return item
