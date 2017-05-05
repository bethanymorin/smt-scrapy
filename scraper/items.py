# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import string
from bs4 import BeautifulSoup


def printable(string_in):
    """ Return a string with any non-printable characters removed
    """
    filtered_chars = []
    printable_chars = set(string.printable)
    for char in string_in:
        if char in printable_chars:
            filtered_chars.append(char)
        else:
            filtered_chars.append(' ')
    return ''.join(filtered_chars)


def get_author_div_text(page, target_class):
    """ Mostly all of the fields in the author profile are nested in the same
        little template pattern. Here's a generic function for pulling out the
        text of a given field class.
    """
    target_div = page.body.find('div', {'class': target_class})
    if target_div:
        target_content_div = target_div.find(
            'div', {'class': 'field-item even'}
        )
        result = target_content_div.text.strip()
        return printable(result)
    return None


def get_author_headshot_url(page):
    image_div = page.body.find('div', {'class': 'field-name-ds-user-picture'})
    if image_div:
        image_div = image_div.find('img')
        return image_div['src']
    return None


def get_author_website_url(page):
    div = page.body.find('div', {'class': 'field-name-field-user-website'})
    if div:
        link = div.find('a')
        return link['href']
    return None


def get_pub_and_author_info(page):
    author_name = None
    pub_date = None
    author_link = None
    pub_date_div = page.body.find(
        'div',
        {'class': 'field-name-post-date-author-name'}
    )

    if pub_date_div:
        author_name = pub_date_div.p.a.text
        pub_date = pub_date_div.p.text.replace(author_name, '').strip()
        author_link = pub_date_div.p.a['href']
    return author_name, author_link, pub_date


def get_author_social_urls(page):
    social_network_link_ids = [
        'facebook',
        'twitter',
        'linkedin',
        'google',
    ]
    social_network_links = {}
    for link_id in social_network_link_ids:
        link_div = page.body.find(
            'div',
            {'class': 'field-name-field-user-%s-url' % link_id}
        )
        if link_div:
            link_content_div = link_div.find(
                'div',
                {'class': 'field-item even'}
            )
            social_network_links[link_id] = link_content_div.a['href']
        else:
            social_network_links[link_id] = None
    return social_network_links


def get_meta_description(page):
    for m in page.head.find_all('meta'):
        if m.get('name') == 'description':
            return printable(m['content'])
    return None


def get_story_body(page):
    body_div = page.body.find('div', {'class': 'field-name-body'})
    body_content_div = body_div.find('div', {'property': 'content:encoded'})
    return printable(body_content_div.decode_contents(formatter="html"))


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

    def process(self, response, db_data):
        """ Stash different parts of the page in the correct property for this object
        """
        html = BeautifulSoup(response.body, "html.parser")
        self['page_type'] = 'contributor profile'
        self['url'] = response.url
        self['bio'] = get_author_div_text(html, 'field-name-field-user-biography')
        self['fullname'] = get_author_div_text(html, 'field-name-user-full-name')
        self['company_name'] = get_author_div_text(html, 'field-name-field-user-company-name')
        self['job_title'] = get_author_div_text(html, 'field-name-field-user-job-title')
        self['headshot_url'] = get_author_headshot_url(html)
        self['website'] = get_author_website_url(html)

        social_link_urls = get_author_social_urls(html)
        self['facebook_url'] = social_link_urls['facebook']
        self['twitter_url'] = social_link_urls['twitter']
        self['linkedin_url'] = social_link_urls['linkedin']
        self['google_url'] = social_link_urls['google']
        self['email'] = db_data['email']
        self['uid'] = db_data['uid']


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

    def process(self, response, db_data):
        """ Stash different parts of the page in the correct property for this object
        """
        html = BeautifulSoup(response.body, "html.parser")
        self['page_type'] = 'article'
        self['url'] = response.url
        self['title'] = html.head.title.text
        self['canonical_url'] = html.head.find('link', rel='canonical')['href']
        self['meta_description'] = get_meta_description(html)
        self['story_title'] = html.body.find('div', property='dc:title').h3.a.text
        (
            self['byline'],
            self['contributor_profile_url'],
            self['pub_date']
        ) = get_pub_and_author_info(html)
        self['body'] = get_story_body(html)
        self['changed'] = db_data['changed']
        self['node_id'] = db_data['nid']
        self['contributor_email'] = db_data['user_email']
        self['contributor_uid'] = db_data['uid']
        self['legacy_content_type'] = db_data['content_type']
