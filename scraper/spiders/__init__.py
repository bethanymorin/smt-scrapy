from bs4 import BeautifulSoup
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scraper.items import SmtArticleItem, SmtContributorProfileItem
from scraper.utils import (
    get_nodes_to_export_from_db,
    get_author_urls_from_jl,
    write_nodes_to_file,
    get_setting_limits,
    get_out_dir,
    get_meta_description,
    get_author_info,
    get_story_body,
    get_author_div_text,
    get_author_headshot_url,
    get_author_website_url,
    get_author_social_urls,
    get_meta_content,
)
from scraper.db_settings import execution_path
import logging


out_dir = get_out_dir()

logFormatter = logging.Formatter("%(asctime)s\t[%(levelname)s]\t%(message)s")
rootLogger = logging.getLogger()

logging.basicConfig(level=logging.DEBUG)
fileHandler = logging.FileHandler('%s/log' % out_dir)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

execution_script_path = execution_path


def update_url_feed(url, spider):
    logging.info("parsed url: %s" % url)


class SmtStories(CrawlSpider):
    ''' CrawlSpider class for crawling the socialmediatoday.com site story pages

        Crawler is initialized based on command line input, see READEM for
        details and instructions
    '''
    name = "stories"

    # get database parameters
    limit, offset = get_setting_limits()

    # query for the URLs for nodes to scrape in this run
    db_nodes = get_nodes_to_export_from_db(0, limit=limit, offset=offset)

    # write the URLS for stories to scrape to a local file
    write_nodes_to_file(db_nodes, 'articles')

    allowed_domains = ["socialmediatoday.com"]

    # set start URL to the file we wrote
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
        html = BeautifulSoup(response.body, "html.parser")

        item = SmtArticleItem()
        item['page_type'] = 'article'
        item['url'] = response.url
        item['title'] = html.head.title.text
        item['canonical_url'] = html.head.find('link', rel='canonical')['href']
        item['meta_description'] = get_meta_description(html)
        item['story_title'] = html.body.find('section', id='section-content').find('div', property="dc:title").h3.text
        item['byline'], item['contributor_profile_url'] = get_author_info(html)
        item['body'] = get_story_body(html)
        item['node_id'] = db_data['nid']
        item['contributor_email'] = db_data['user_email']
        item['contributor_uid'] = db_data['uid']
        item['legacy_content_type'] = db_data['content_type']
        item['changed'] = get_meta_content(html, 'article:modified_time', '1776-07-04T06:30:00-00:00')
        item['pub_date'] = get_meta_content(html, 'article:published_time', '1776-07-04T06:30:00-00:00')
        update_url_feed(response.url, spider=self)
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
        html = BeautifulSoup(response.body, "html.parser")

        item = SmtContributorProfileItem()
        item['page_type'] = 'contributor profile'
        item['url'] = response.url
        item['bio'] = get_author_div_text(html, 'field-name-field-user-biography')
        item['fullname'] = get_author_div_text(html, 'field-name-user-full-name')
        item['company_name'] = get_author_div_text(html, 'field-name-field-user-company-name')
        item['job_title'] = get_author_div_text(html, 'field-name-field-user-job-title')
        item['headshot_url'] = get_author_headshot_url(html)
        item['website'] = get_author_website_url(html)

        social_link_urls = get_author_social_urls(html)
        item['facebook_url'] = social_link_urls['facebook']
        item['twitter_url'] = social_link_urls['twitter']
        item['linkedin_url'] = social_link_urls['linkedin']
        item['google_url'] = social_link_urls['google']
        item['email'] = db_data['email']
        item['uid'] = db_data['uid']

        update_url_feed(response.url, spider=self)

        return item
