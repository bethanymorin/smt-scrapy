import scrapy

from bs4 import BeautifulSoup

from scraper.items import SmtArticleItem, SmtContributorProfileItem
from scraper import utils
from scraper import node_data


class SmtStories(scrapy.Spider):
    """
    Spider class for crawling the socialmediatoday.com site story pages. This
    also looks for author links and parses the author profile pages.

    Run on the command line with scrapy crawl stories
    """
    name = "stories"
    allowed_domains = ['socialmediatoday.com', 'platform.sh']

    # Read the node data and urls from nodes.json and urls.txt files.
    node_data_reader = node_data.Reader()

    # The urls of the story pages.
    start_urls = node_data_reader.get_urls()

    def parse(self, response):
        """
        Parse a story page and look for author links.

        Yields requests for author profile pages and story items.
        """
        self.logger.info('Parsing {}'.format(response.url))

        db_data = self.node_data_reader.get_node_data_by_url(response.url)
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

        # If we found an author URL, then make a request for the author
        # profile page.
        if item['contributor_profile_url'] is not None:
            author_url = item['contributor_profile_url']

            # Extra context that we want in the author export that doesn't
            # exist on the author profile page. Email and uid come from the
            # database.
            author_info = {
                'url': author_url,
                'uid': item['contributor_uid'],
                'email': item['contributor_email'],
            }

            self.logger.info('Yielding profile url: {}'.format(author_url))

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
        """
        self.logger.info('Parsing {}'.format(response.url))

        # This is the uid and email we provided in the request meta when
        # parsing the story page.
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
