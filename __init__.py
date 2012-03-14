# -*- coding: utf-8 -*-

from datetime import datetime
from time import sleep
import random
import urllib2
from lxml import etree
from twitter_oauth_op import post2twi
from douban_oauth_op import post2douban

tweets_count_max = 3

file_name = 'pinbpopxmltmp.xml'
xml_keys = {'item': '{http://purl.org/rss/1.0/}item',
            'title': '{http://purl.org/rss/1.0/}title',
            'link': '{http://purl.org/rss/1.0/}link'}
pinbpop_url = 'http://feeds.pinboard.in/rss/popular/'
    

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

def parse_pop_xml(count):
    doc = etree.parse(file_name)
    items = doc.findall(xml_keys['item'])
    random.shuffle(items) # disrupt the list sort
    ret = []
    for item in items[:count]:
        title = item.find(xml_keys['title']).text.encode('utf-8').strip()
        link = item.find(xml_keys['link']).text.encode('utf-8').strip()
        ret.append({'title':title, 'link':link})
    return ret

def add_status(title, link):
    content = '%s %s' % (title, link)
    if len(content) > 140:
        tlen = len(content) - len(link) - 1
        content = '%s %s' % (title[:tlen], link)
    print content
    post2twi(content):
    post2douban(content)


if __name__ == '__main__':
    download_pop_xml()
    items = parse_pop_xml(count=tweets_count_max)
    for item in items:
        add_status(item['title'], item['link'])
        sleep(1)
    print '=================== Process finished %s =========================' % datetime.now().strftime('%Y%m%d %H:%M')
