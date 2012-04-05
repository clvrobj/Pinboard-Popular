# -*- coding: utf-8 -*-

from datetime import datetime
from time import sleep
import random
import urllib2
from lxml import etree
from pymongo import Connection
from twitter_oauth_op import post2twi
from douban_oauth_op import post2douban

tweets_count_max = 3

file_name = 'pinbpopxmltmp.xml'
xml_keys = {'item': '{http://purl.org/rss/1.0/}item',
            'title': '{http://purl.org/rss/1.0/}title',
            'link': '{http://purl.org/rss/1.0/}link'}
pinbpop_url = 'http://feeds.pinboard.in/rss/popular/'

def init_mongo():
    from local_conf import DATABASE
    connection = Connection(host=DATABASE['HOST'], port=DATABASE['PORT'], network_timeout=2)
    db = connection[DATABASE['NAME']]
    db.authenticate(DATABASE['USER'], DATABASE['PASSWORD'])
    collection = db['bookmarks']
    return connection, db, collection

def check_tweeted_link(collection, link):
    links = collection.find({'link':link})
    return True if links.count() > 0 else False

def save_tweeted_link(collection, link, title):
    collection.insert({'link':link, 'title':title})

def download_pop_xml():
    url = pinbpop_url
    post_data = ''
    headers = {}
    req = urllib2.Request(url, post_data, headers)
    response = urllib2.urlopen(req)

    data = response.read()
    w = open(file_name, 'w')
    w.write(data)
    w.close()

def parse_pop_xml(collection, count):
    doc = etree.parse(file_name)
    items = doc.findall(xml_keys['item'])
    ret = []
    i = 0
    while len(ret) < count and i < len(items):
        item = items[i]
        link = item.find(xml_keys['link']).text.encode('utf-8').strip()
        if not check_tweeted_link(collection, link):
            title = item.find(xml_keys['title']).text.encode('utf-8').strip()
            ret.append({'title':title, 'link':link})
        i += 1
    return ret

def add_status(collection, title, link):
    save_tweeted_link(collection, link, title)
    content = '%s %s' % (title, link)
    if len(content) > 140:
        tlen = len(content) - len(link) - 1
        content = '%s %s' % (title[:tlen], link)
    print content
    post2twi(content)
    post2douban(content)


if __name__ == '__main__':
    conn, db, collection = init_mongo()
    download_pop_xml()
    items = parse_pop_xml(collection, count=tweets_count_max)
    for item in items:
        add_status(collection, item['title'], item['link'])
        sleep(1)
    conn.disconnect()
    print '=================== Process finished %s =========================' % datetime.now().strftime('%Y%m%d %H:%M')
