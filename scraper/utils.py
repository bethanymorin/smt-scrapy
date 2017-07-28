import db_settings
import MySQLdb
import logging
import json
import string
import codecs


class AbstractNodeData(object):

    def __init__(self, nodes_filename='nodes.json', urls_filename='urls.txt', encoding='latin-1'):
        self._data = None
        self._urls = None
        self.nodes_filename = nodes_filename
        self.urls_filename = urls_filename
        self.encoding = encoding

    def get_data(self):
        if self._data is None:
            self._data = self._query_data()

        return self._data

    def get_urls(self):
        if self._urls is None:
            self._urls = self._query_urls()

        return self._urls

    def _query_data(self):
        return {}

    def _query_urls(self):
        return []


class NodeDataReader(AbstractNodeData):

    def _query_data(self):
        with codecs.open(self.nodes_filename, 'rb') as fp:
            all_node_data = json.load(fp, encoding=self.encoding)

        return all_node_data

    def _query_urls(self):
        with codecs.open(self.urls_filename, 'rb', encoding=self.encoding) as fp:
            urls = fp.readlines()

        return [x.strip() for x in urls]


class NodeDataWriter(AbstractNodeData):

    def write_nodes_json(self):
        with codecs.open(self.nodes_filename, 'wb') as fp:
            json.dump(self.get_data(), fp, encoding=self.encoding)

    def write_urls_txt_file(self):
        with codecs.open(self.urls_filename, 'wb', encoding=self.encoding) as fp:
            fp.write('\n'.join(self.get_urls()))

    def _get_connection():
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

    def _query_data(self):
        # this query gets back the identifying information for the posts we want
        # as well as the node and full path URLs that we can use to get the current
        # actual HTML page
        db = self._get_connection()
        node_query = (
            "select n.nid, user.uid, user.mail, n.changed, "
            "n.type as content_type, u.alias, u.source "
            "from node n "
            "join users user on n.uid = user.uid "
            "join url_alias u on u.source = CONCAT('node/', n.nid) "
            "where n.type ='post' and n.status = 1 "
            "and u.pid=(select pid from url_alias where source = u.source "
            "order by pid desc limit 1) "
            "order by n.changed DESC"
        )

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
            nodes['%s%s' % (db_settings.site_url, alias)] = node_data
        db.close()

        return nodes

    def _query_urls(self):
        return self.get_data().keys()


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
