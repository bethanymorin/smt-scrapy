import db_settings
import MySQLdb
import logging
import json
import os
import string


# set up and database utils
def get_db_connection():
    """ Establish a mysql database connection from given db_settings file values
        Return the database connection object
    """
    kwargs = {}
    if db_settings.mysql_pw:
        kwargs['passwd'] = db_settings.mysql_pw
    if db_settings.mysql_user:
        kwargs['user'] = db_settings.mysql_user
    if db_settings.mysql_host:
        kwargs['host'] = db_settings.mysql_host
    if db_settings.mysql_db:
        kwargs['db'] = db_settings.mysql_db
    if db_settings.mysql_port:
        kwargs['port'] = db_settings.mysql_port

    logging.debug("Connecting to mysql: %s" % kwargs)
    db = MySQLdb.connect(**kwargs)
    return db


def get_nodes_to_export_from_db(changed_epoch, limit=None, offset=None):
    # this query gets back the identifying information for the posts we want
    # as well as the node and full path URLs that we can use to get the current
    # actual HTML page
    db = get_db_connection()
    logging.info("Building query for stories changed from %s" % changed_epoch)
    node_query = (
        "select n.nid, user.uid, user.mail, n.changed, "
        "n.type as content_type, u.alias, u.source "
        "from node n "
        "join users user on n.uid = user.uid "
        "join url_alias u on u.source = CONCAT('node/', n.nid) "
        "where n.type ='post' and n.status = 1 "
        "and u.pid=(select pid from url_alias where source = u.source "
        "order by pid desc limit 1) "
        "and n.changed > %d "
        "order by n.changed DESC"
    )
    logging.debug("Query is: %s" % node_query)
    node_query = node_query % changed_epoch
    if limit:
        node_query = node_query + ' limit %s' % limit
    if offset:
        node_query = node_query + ' offset %s' % offset
    node_cursor = db.cursor()
    node_cursor.execute(node_query)
    nodes = {}
    for nid, uid, mail, changed, content_type, alias, source in node_cursor:
        node_data = {
            'nid': nid,
            'uid': uid,
            'user_email': mail,
            'changed': changed,
            'content_type': content_type,
            'node_url_path': source,
            'url_path': alias
        }
        nodes['http://www.socialmediatoday.com/%s' % alias] = node_data
    db.close()
    return nodes


def get_author_urls_from_jl(source_file='output/stories.jl'):
    author_links = {}
    if os.path.exists(source_file):
        with open(source_file) as file:
            for line in file:
                data = json.loads(line)
                author_links[data['contributor_profile_url']] = {
                    'url': data['contributor_profile_url'],
                    'uid': data['contributor_uid'],
                    'email': data['contributor_email'],
                }
    return author_links


def write_nodes_to_file(nodes, filename):
    f = open('%s.html' % filename, 'w+')
    for url in nodes.keys():
        f.write('<a href="%s">%s</a><br />' % (url, url))
    f.close()


def get_setting_limits():
    settings = open('.crawl_smt/settings.txt', 'r').read().split(',')
    limit = int(settings[0])
    offset = int(settings[1])
    if limit == 0:
        limit = None
    if offset == 0:
        offset = None
    return limit, offset


def get_out_dir():
    settings = open('.crawl_smt/settings.txt', 'r').read().split(',')
    out_dir = settings[2]
    return out_dir


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
