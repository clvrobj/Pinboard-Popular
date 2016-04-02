# -*- coding: utf-8 -*-

from datetime import datetime
from time import sleep
import random
import urllib2
from lxml import etree
from twitter_oauth_op import post2twi
from douban_oauth_op import post2douban

TWEETS_COUNT_MAX = 3

file_name = 'pinbpopxmltmp.xml'
xml_keys = {'item': '{http://purl.org/rss/1.0/}item',
            'title': '{http://purl.org/rss/1.0/}title',
            'link': '{http://purl.org/rss/1.0/}link',
            'description': '{http://purl.org/rss/1.0/}description'}
pinbpop_url = 'http://feeds.pinboard.in/rss/popular/'

def init_mongo():
    try:
        from pymongo import MongoClient
        from local_conf import DATABASE
        client = MongoClient(host=DATABASE['HOST'], port=DATABASE['PORT'])
        db = client[DATABASE['NAME']]
        db.authenticate(DATABASE['USER'], DATABASE['PASSWORD'])
        collection = db['bookmarks']
        return client, collection
    except ImportError:
        return None, None

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

def parse_pop_xml(max_count, collection):
    doc = etree.parse(file_name)
    items = doc.findall(xml_keys['item'])
    ret = []
    i = 0
    while len(ret) < max_count and i < len(items):
        item = items[i]
        link = item.find(xml_keys['link']).text.encode('utf-8').strip()
        if collection and check_tweeted_link(collection, link):
            i += 1
            continue
        title = item.find(xml_keys['title']).text.encode('utf-8').strip()
        if title == 'Twitter':
            title = item.find(xml_keys['description']).text.encode('utf-8').strip()
        ret.append({'title':title, 'link':link})
        i += 1
    return ret

def add_status(title, link, collection):
    content = '%s %s' % (title, link)
    if len(content) > 140:
        tlen = len(content) - len(link) - 1
        content = '%s %s' % (title[:tlen], link)
    print content
    post2twi(content)
    # post2douban(content)
    if collection:
        save_tweeted_link(collection, link, title)


if __name__ == '__main__':
    download_pop_xml()
    conn, collection = init_mongo()
    items = parse_pop_xml(TWEETS_COUNT_MAX, collection)
    for item in items:
        add_status(item['title'], item['link'], collection)
        sleep(1)
    if conn:
        conn.disconnect()
    print '=================== Process finished %s =========================' % datetime.now().strftime('%Y%m%d %H:%M')
