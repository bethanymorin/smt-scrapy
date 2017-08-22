import scrapy

from scraper.items import SmtArticleItem, SmtContributorProfileItem


# Twitter gets special treatment below.
SOCIAL_NETWORKS = {
    'facebook': 'div.field-name-field-user-facebook-url div.field-item a::attr(href)',
    'linkedin': 'div.field-name-field-user-linkedin-url div.field-item a::attr(href)',
    'google': 'div.field-name-field-user-google-url div.field-item a::attr(href)',
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

            category = row.css('.scrapy-category a::text').extract_first()

            metadata = {
                'nid': node_link.css('::text').extract_first(),
                'node_url': node_url,
                'uid': user_link.css('::text').extract_first(),
                'user_url': user_url,
                'category': category,
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

        # Shortcuts to the head and body html tags.
        head = response.css('head')
        body = response.css('body')

        item = SmtArticleItem()
        item['page_type'] = 'article'
        item['url'] = response.url
        item['node_id'] = response.meta['nid']
        item['contributor_uid'] = response.meta['uid']
        item['category'] = response.meta['category'] or ''

        title = head.css('title::text').extract_first() or ''
        # Remove the site name and pipe from the page title.
        title = title.replace(' | Social Media Today', '')
        item['title'] = title.strip()

        canonical_url = head.css('link[rel=canonical]::attr(href)').extract_first() or ''
        item['canonical_url'] = canonical_url.strip()

        desc = head.css('meta[name=description]::attr(content)').extract_first() or ''
        item['meta_description'] = desc.strip()

        changed = head.css('meta[property="article:modified_time"]::attr(content)').extract_first() or ''
        item['changed'] = changed.strip()

        pub_date = head.css('meta[property="article:published_time"]::attr(content)').extract_first() or ''
        item['pub_date'] = pub_date.strip()

        story_title = body.css('section#section-content div[property="dc:title"] h3::text').extract_first() or ''
        item['story_title'] = story_title.strip()

        author_link = body.css('div.field-name-post-date-author-name .field-item p a')
        byline = author_link.css('::text').extract_first() or ''
        item['byline'] = byline.strip()
        contributor_profile_url = author_link.css('::attr(href)').extract_first() or ''
        item['contributor_profile_url'] = contributor_profile_url.strip()

        body_content = body.css('div.field-name-body div[property="content:encoded"]').extract_first() or ''
        item['body'] = body_content.strip()

        yield item

    def parse_author_page(self, response):
        """
        Parse an author profile page.

        Needs uid passed in from response.meta.
        """
        self.logger.info('Parsing author {}'.format(response.url))

        # Shortcut to the html body tag.
        body = response.css('body')

        item = SmtContributorProfileItem()
        item['uid'] = response.meta['uid']
        item['page_type'] = 'contributor profile'
        item['url'] = response.url

        # First name is plain text.
        first_name = body.css('.scrapy-first-name::text').extract_first() or ''
        item['first_name'] = first_name.strip()

        # Last name is plain text.
        last_name = body.css('.scrapy-last-name::text').extract_first() or ''
        item['last_name'] = last_name.strip()

        # Company name is plain text.
        company_name = body.css('.field-name-field-user-company-name .field-item::text').extract_first() or ''
        item['company_name'] = company_name.strip()

        # Job title is plain text.
        job_title = body.css('.field-name-field-user-job-title .field-item::text').extract_first() or ''
        item['job_title'] = job_title.strip()

        # Absolute URL field.
        headshot_url = body.css('.field-name-ds-user-picture img::attr(src)').extract_first() or ''
        item['headshot_url'] = headshot_url.strip()

        # Absolute URL field.
        website = body.css('.field-name-field-user-website .field-item a::attr(href)').extract_first() or ''
        item['website'] = website.strip()

        # Bio is the only html field.
        bio = body.css('.field-name-field-user-biography .field-item').extract_first() or ''
        item['bio'] = bio.strip()

        # Absolute URL fields.
        for network_key, selector in SOCIAL_NETWORKS.items():
            href = body.css(selector).extract_first() or ''
            item[network_key] = href.strip()

        # Get the twitter URL and cut it down to just the handle because that's what we expect in divesite.
        twitter_selector = 'div.field-name-field-user-twitter-url div.field-item a::attr(href)'
        twitter_url = body.css(twitter_selector).extract_first() or ''
        twitter_handle = twitter_url.replace('https://twitter.com/', '').split('?')[0]
        item['twitter_handle'] = twitter_handle.strip()

        yield item
