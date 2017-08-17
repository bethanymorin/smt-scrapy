import scrapy

from scraper.items import SmtArticleItem, SmtContributorProfileItem

USER_FIELD_MAP = {
    'bio': 'field-name-field-user-biography',
    'fullname': 'field-name-user-full-name',
    'company_name': 'field-name-field-user-company-name',
    'job_title': 'field-name-field-user-job-title'
}

SOCIAL_NETWORKS = {
    'facebook':
        'div.field-name-field-user-facebook-url div.field-item even '
        'a::attr(href)',
    'twitter':
        'div.field-name-field-user-twitter-url div.field-item even '
        'a::attr(href)',
    'linkedin':
        'div.field-name-field-user-linkedin-url div.field-item even '
        'a::attr(href)',
    'google':
        'div.field-name-field-user-google-url div.field-item even '
        'a::attr(href)',
}


class SocialMediaToday(scrapy.Spider):
    """
    Spider class for crawling the socialmediatoday.com site story pages. This
    also looks for author links and parses the author profile pages.

    Run on the command line with scrapy crawl stories
    """
    name = "socialmediatoday"
    allowed_domains = ['socialmediatoday.com', 'platform.sh']

    def start_requests(self):
        for url in self.settings['START_URLS']:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        self.logger.info('Parsing {}'.format(response.url))

        # Look for pagination.
        next_page = response.css('.pager-next a::attr(href)').extract_first()
        if next_page is not None:
            self.logger.info(
                'Adding a new all-stories page: {}'.format(next_page))
            yield response.follow(
                next_page,
                callback=self.parse
            )

        # Parse the rows. Add node and user pages
        rows = response.css('tr.scrapy-node')

        for row in rows:
            node_link = row.css('td.scrapy-node-id a')
            user_link = row.css('td.scrapy-user-id a')

            node_url = node_link.css('::attr(href)').extract_first()
            user_url = user_link.css('::attr(href)').extract_first()

            metadata = {
                'nid': node_link.css('::text').extract_first(),
                'node_url': node_url,
                'uid': user_link.css('::text').extract_first(),
                'user_url': user_url,
            }

            self.logger.info('Adding {} and {}'.format(node_url, user_url))
            yield response.follow(
                node_url,
                callback=self.parse_story_page,
                meta=metadata
            )

            yield response.follow(
                user_url,
                callback=self.parse_author_page,
                meta=metadata
            )

    def parse_story_page(self, response):
        """
        Parse a story page and look for author links.

        Yields requests for author profile pages and story items.

        Needs the following from response.meta:
        nid
        uid

        """
        self.logger.info('Parsing story {}'.format(response.url))

        head = response.css('head')
        body = response.css('body')

        item = SmtArticleItem()
        item['page_type'] = 'article'
        item['url'] = response.url
        item['node_id'] = response.meta['nid']
        item['title'] = head.css('title::text').extract_first()
        item['contributor_uid'] = response.meta['uid']

        canonical_url = head.css(
            'link[rel=canonical]::attr(href)').extract_first()
        item['canonical_url'] = canonical_url or ''

        desc = head.css(
            'meta[name=description]::attr(content)').extract_first()
        item['meta_description'] = desc or ''

        changed = head.css(
            'meta[property="article:modified_time"]::attr(content)')\
            .extract_first()
        item['changed'] = changed or ''

        pub_date = head.css(
            'meta[property="article:published_time"]::attr(content)')\
            .extract_first()
        item['pub_date'] = pub_date or ''

        story_title = body.css(
            'section#section-content div[property="dc:title"] h3::text')\
            .extract_first()
        item['story_title'] = story_title or ''

        author_link = body.css(
            'div.field-name-post-date-author-name .field-item p a')
        item['byline'] = author_link.css('::text').extract_first() or ''
        item['contributor_profile_url'] = author_link.css(
            '::attr(href)').extract_first() or ''

        body_content = body.css(
            'div.field-name-body div[property="content:encoded"]')\
            .extract_first()
        item['body'] = body_content or ''

        yield item

    def parse_author_page(self, response):
        """
        Parse an author profile page.

        Needs uid passed in from response.meta.
        """
        self.logger.info('Parsing author {}'.format(response.url))

        body = response.css('body')

        item = SmtContributorProfileItem()
        item['uid'] = response.meta['uid']
        item['page_type'] = 'contributor profile'
        item['url'] = response.url

        for item_key, field_key in USER_FIELD_MAP.items():
            # Default to empty string.
            item[item_key] = ''
            full_selector = 'div.{} div.field-item::text'.format(field_key)
            field_value = body.css(full_selector).extract_first()
            if field_value:
                item[item_key] = field_value.strip()

        bio = body.css('.field-name-field-user-biography div div::text').extract_first() or ''
        fullname = body.css('.field-name-user-full-name div div a strong::text').extract_first() + response.css(
            '.field-name-user-full-name div div a::text'
        ).extract_first() or ''
        job_title = body.css('.field-name-field-user-job-title div div.field-item::text').extract_first() or ''
        company_name = body.css('.field-name-field-user-company-name div.field-item::text').extract_first() or ''
        twitter = body.css('.field-name-field-user-twitter-url div div.field-item a::text').extract_first() or ''
        facebook = body.css('.field-name-field-user-facebook-url div div.field-item a::text').extract_first() or ''
        linkedin = body.css('.field-name-field-user-linkedin-url div div.field-item a::text').extract_first() or ''
        google = body.css('.field-name-field-user-google-url div div.field-item a::text').extract_first() or ''

        item['google'] = google.strip()
        item['linkedin'] = linkedin.strip()
        item['facebook'] = facebook.strip()
        item['twitter'] = twitter.strip()
        item['company_name'] = company_name.strip()
        item['job_title'] = job_title.strip()
        item['fullname'] = fullname.strip()
        item['bio'] = bio.strip()

        headshot_url = body.css(
            'div.field-name-ds-user-picture img::attr(src)').extract_first()
        item['headshot_url'] = headshot_url or ''

        website = body.css(
            'div.field-name-field-user-website .field-item a::attr(href)')\
            .extract_first()
        item['website'] = website or ''

        for network_key, selector in SOCIAL_NETWORKS.items():
            # Default to empty string.
            item[network_key] = ''

            href = body.css(selector).extract_first()

            if href:
                item[network_key] = href.strip()

        yield item
