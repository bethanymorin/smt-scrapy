import string


# page parsing utils
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


def get_author_info(page):
    author_name = None
    author_link = None
    pub_div = page.body.find(
        'div',
        {'class': 'field-name-post-date-author-name'}
    )

    if pub_div:
        author_name = pub_div.p.a.text
        author_link = pub_div.p.a['href']
    return author_name, author_link


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


def get_meta_content(html, property_name, default_return):
    meta_property = html.head.find('meta', {'property': property_name})
    if meta_property:
        content = meta_property.get('content', default_return)
        return content
    return default_return
