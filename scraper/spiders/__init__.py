import scrapy

from bs4 import BeautifulSoup

from scraper.items import SmtArticleItem, SmtContributorProfileItem
from scraper import utils


class SmtStories(scrapy.Spider):
    ''' CrawlSpider class for crawling the socialmediatoday.com site story pages

        Crawler is initialized based on command line input, see READEM for
        details and instructions
    '''
    name = "stories"
    allowed_domains = ['socialmediatoday.com', 'platform.sh']

    node_data_reader = utils.NodeDataReader()

    start_urls = node_data_reader.get_urls()
    db_nodes = node_data_reader.get_data()

    def parse(self, response):
        """
        Parse a story page and look for author links.

        :param response:
        :return:
        """
        self.logger.info('Started crawling {}'.format(response.url))

        db_data = self.db_nodes[response.url]
        html = BeautifulSoup(response.body, 'lxml')

        item = SmtArticleItem()
        item['page_type'] = 'article'
        item['url'] = response.url
        item['title'] = html.head.title.text
        item['canonical_url'] = html.head.find('link', rel='canonical')['href']
        item['meta_description'] = utils.get_meta_description(html)
        item['story_title'] = html.body.find('section', id='section-content').find('div', property="dc:title").h3.text
        item['byline'], item['contributor_profile_url'] = utils.get_author_info(html)
        item['body'] = utils.get_story_body(html)
        item['node_id'] = db_data['nid']
        item['contributor_email'] = db_data['user_email']
        item['contributor_uid'] = db_data['uid']
        item['legacy_content_type'] = db_data['content_type']
        item['changed'] = utils.get_meta_content(html, 'article:modified_time', '1776-07-04T06:30:00-00:00')
        item['pub_date'] = utils.get_meta_content(html, 'article:published_time', '1776-07-04T06:30:00-00:00')

        if item['contributor_profile_url'] is not None:

            author_url = item['contributor_profile_url']
            author_info = {
                'url': author_url,
                'uid': item['contributor_uid'],
                'email': item['contributor_email'],
            }

            self.logger.info('Yielding profile url for crawling: {}'.format(author_url))

            yield response.follow(
                author_url,
                callback=self.parse_author_page,
                meta=author_info
            )
        else:
            self.logger.error('Cannot find author url for {}'.format(response.url))

        yield item

    def parse_author_page(self, response):
        """
        Parse an author profile page.

        :param response:
        :return:
        """
        db_data = response.meta
        html = BeautifulSoup(response.body, 'lxml')

        item = SmtContributorProfileItem()
        item['page_type'] = 'contributor profile'
        item['url'] = response.url
        item['bio'] = utils.get_author_div_text(html, 'field-name-field-user-biography')
        item['fullname'] = utils.get_author_div_text(html, 'field-name-user-full-name')
        item['company_name'] = utils.get_author_div_text(html, 'field-name-field-user-company-name')
        item['job_title'] = utils.get_author_div_text(html, 'field-name-field-user-job-title')
        item['headshot_url'] = utils.get_author_headshot_url(html)
        item['website'] = utils.get_author_website_url(html)

        social_link_urls = utils.get_author_social_urls(html)
        item['facebook_url'] = social_link_urls['facebook']
        item['twitter_url'] = social_link_urls['twitter']
        item['linkedin_url'] = social_link_urls['linkedin']
        item['google_url'] = social_link_urls['google']
        item['email'] = db_data['email']
        item['uid'] = db_data['uid']

        yield item
