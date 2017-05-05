import db_settings
import MySQLdb
import logging
import json
import os


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


def get_nodes_to_export_from_db(changed_epoch, limit=None):
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
        "order by n.changed DESC "
    )
    logging.debug("Query is: %s" % node_query)
    node_query = node_query % changed_epoch
    if limit:
        node_query = node_query + 'limit %s' % limit
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


def get_author_urls_from_jl(source_file='smt_stories.jl'):
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
