# -*- coding: utf-8 -*-

import time
from datetime import datetime
import base64
import random
import string
import urllib2
from lxml import etree
from douban_oauth_op import post2douban

file_name = 'pinbpopxmltmp.xml'
xml_keys = {'item': '{http://purl.org/rss/1.0/}item',
            'title': '{http://purl.org/rss/1.0/}title',
            'link': '{http://purl.org/rss/1.0/}link'}
pinbpop_url = 'http://feeds.pinboard.in/rss/popular/'
post_twi_url = 'https://api.twitter.com/1/statuses/update.json'

from local_conf import *
consumer_key = CONSUMER_KEY
consumer_secret = CONSUMER_SECRET
token = TOKEN
token_secret = TOKEN_SECRET

def sign_request(raw, key=None):
    from hashlib import sha1
    from hmac import new as hmac
    # If you dont have a token yet, the key should be only "CONSUMER_SECRET&"
    key = key or "%s&%s" % (consumer_secret, token_secret) 
    return "%s" % hmac(key, raw, sha1).digest().encode('base64')[:-1]

def encode_uri(s):
    return urllib2.quote(s, safe='~()*!.')

def post2twi(status):
    # NOTICE info below should keep secret
    post_data = {'include_entities':'true', 'trim_user':'true', 'status':status}
    header = {}
    headers_data = {'oauth_consumer_key':consumer_key,
                    'oauth_nonce':'', # calc b4 every req
                    #'oauth_signature':'', # calc b4 every req Notice this should be gen by all the params
                    'oauth_signature_method':'HMAC-SHA1',
                    'oauth_timestamp':'', # calc b4 every req
                    'oauth_token':token,
                    'oauth_version':'1.0'}
    headers_data['oauth_nonce'] = base64.urlsafe_b64encode(''.join(random.sample(string.letters, 30)))
    headers_data['oauth_timestamp'] = str(int(time.mktime(datetime.now().timetuple())))
    
    # gen signature
    sign_data = {}
    sign_data.update(headers_data)
    sign_data.update(post_data)
    sign_data = ['='.join((encode_uri(k), encode_uri(v))) for k,v in sign_data.items()]
    sign_data.sort()
    sign_data = '&'.join(sign_data)
    sign_data = 'POST&%s&%s' % (encode_uri(post_twi_url), encode_uri(sign_data))
    headers_data['oauth_signature'] = sign_request(sign_data)
    headers_str = ', '.join(['%s="%s"' % (encode_uri(k), encode_uri(v)) for k, v in headers_data.items()])
    headers_str = 'OAuth %s' % headers_str
    header = {'Authorization': headers_str}
    #print header
    
    post_data_str = '&'.join(['%s=%s' % (k, encode_uri(v)) for k,v in post_data.items()])
    #print post_data_str

    res = False
    try:
        req = urllib2.Request(post_twi_url, post_data_str, header)
        response = urllib2.urlopen(req)
        print response.read()
        res = True
        print 'Tweet OK: %s' % status
    except urllib2.HTTPError, e:
        print 'Request error. ', e

    return res

    # to test with curl
    #print "curl --request 'POST' '%s' --data '%s' --header '%s' --verbose" % (post_twi_url, post_data_str, 'Authorization: %s' % headers_str)

    # test the sample from https://dev.twitter.com/docs/auth/creating-signature
    #    t = 'POST&https%3A%2F%2Fapi.twitter.com%2F1%2Fstatuses%2Fupdate.json&include_entities%3Dtrue%26oauth_consumer_key%3Dxvz1evFS4wEEPTGEFPHBog%26oauth_nonce%3DkYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1318622958%26oauth_token%3D370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb%26oauth_version%3D1.0%26status%3DHello%2520Ladies%2520%252B%2520Gentlemen%252C%2520a%2520signed%2520OAuth%2520request%2521'
    #    k = 'kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw&LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE'
    #    print sign_request(t, k)
    

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

def parse_pop_xml():
    doc = etree.parse(file_name)
    items = doc.findall(xml_keys['item'])
    twi_count = 0
    random.shuffle(items) # disrupt the list sort
    for item in items:
        title = item.find(xml_keys['title']).text.encode('utf-8').strip()
        link = item.find(xml_keys['link']).text.encode('utf-8').strip()
        content = '%s %s' % (title, link)
        if len(content) > 140:
            tlen = len(content) - len(link) - 1
            content = '%s %s' % (title[:tlen], link)
        print content
        if post2twi(content):
            post2douban(content)
            twi_count += 1
            from time import sleep
            sleep(1)
        if twi_count >= 6: # 6 tweets at most
            break

if __name__ == '__main__':
    download_pop_xml()
    parse_pop_xml()
    #post2twi('Test tweet2')
    print '=================== Process finished %s =========================' % datetime.now().strftime('%Y%m%d %H:%M')
