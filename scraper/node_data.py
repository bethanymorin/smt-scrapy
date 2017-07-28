"""
This includes a Reader and Writer for node data and URLS.

The Writer queries the database and can write two files.
1. nodes.json: This is a json file of metadata about all nodes that we
    couldn't get from just scraping the page.
2. urls.txt: This contains all story urls, one url per line.

The Writer can be used like so:

    writer = node_data.Writer()
    writer.write_nodes_json()
    writer.write_urls_txt_file()

The database connection details need to be in db_settings.py and the default
output location is in the current directory.

The Reader reads the files output above and provides them in a format that our
scrapy Spider can use.

Use it like so:

    reader = node_data.Reader()
    node_data = reader.get_data()
    start_urls = reader.get_urls()

It expects the files to live in teh same place they were output.
"""

import db_settings
import MySQLdb
import json
import codecs


class AbstractNodeData(object):
    """
    This is a base class for the Reader and Writer.

    They provide a common API for get_data() and get_urls().
    """

    def __init__(self, nodes_filename='nodes.json', urls_filename='urls.txt', encoding='latin-1'):
        """
        Set some defaults for lazy loading private storage and defining where
        the files live.

        :param str nodes_filename: Path and filename of the nodes.json file.
        :param str urls_filename: Path and filename of the urls.txt file.
        :param str encoding: File encoding.
        """
        self._data = None
        self._urls = None
        self.nodes_filename = nodes_filename
        self.urls_filename = urls_filename
        self.encoding = encoding

    def get_node_data_by_url(self, url):
        """
        Get the data for a single node given a url.

        :param str url: The full url of the node.
        :return: The data about the node.
        :rtype: dict
        """
        return self.get_data()[url]

    def get_data(self):
        """
        Get the node data. Calls the subclass's private method and caches it.

        :return: The node data, keyed by the node's full url.
        :rtype: dict
        """
        if self._data is None:
            self._data = self._query_data()

        return self._data

    def get_urls(self):
        """
        Get the urls of stories to provide to the spider. Calls the subclass's
        private method and caches it.

        :return: A list of urls.
        :rtype: list
        """
        if self._urls is None:
            self._urls = self._query_urls()

        return self._urls

    def _query_data(self):
        """
        Implement this in the subclass to return the dict of node data keyed
        by url.
        """
        return {}

    def _query_urls(self):
        """
        Implement this in the subclass to return the list of urls to stories.
        """
        return []


class Reader(AbstractNodeData):
    """
    The node data Reader. Opens the files and provides the node data and urls.
    """

    def _query_data(self):
        """
        Retrieve the node data from the nodes.json file.
        """
        with codecs.open(self.nodes_filename, 'rb') as fp:
            all_node_data = json.load(fp, encoding=self.encoding)

        return all_node_data

    def _query_urls(self):
        """
        Retrieves the urls from urlst.txt.
        """
        with codecs.open(self.urls_filename, 'rb', encoding=self.encoding) as fp:
            urls = fp.readlines()

        return [x.strip() for x in urls]


class Writer(AbstractNodeData):
    """
    The node data writer. This queries the database and writes the files.
    """

    def write_nodes_json(self):
        """
        Write the nodes.json file.
        """
        with codecs.open(self.nodes_filename, 'wb') as fp:
            json.dump(self.get_data(), fp, encoding=self.encoding)

    def write_urls_txt_file(self):
        """
        Write the urls.txt file.
        """
        with codecs.open(self.urls_filename, 'wb', encoding=self.encoding) as fp:
            fp.write('\n'.join(self.get_urls()))

    def _get_connection(self):
        """
        Establish a mysql database connection from given db_settings values

        :return: The database connection object.
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

        return MySQLdb.connect(**kwargs)

    def _query_data(self):
        """
        Retrieve the node data by querying the database.
        """
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
        """
        Retrieve the urls of the nodes by using the data from the database.
        """
        return self.get_data().keys()
