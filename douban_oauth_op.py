# -*- coding: utf-8 -*-

import base64
import time
import random
import string
import urllib2
from datetime import datetime
import httplib

douban_req_token_url = 'http://www.douban.com/service/auth/request_token'
douban_access_token_url = 'http://www.douban.com/service/auth/access_token'
douban_say_url = 'http://api.douban.com/miniblog/saying'
douban_user_id = '47529301'
sign_method = 'HMAC-SHA1'

from local_conf import *
api_key = DB_API_KEY
api_key_secret = DB_API_KEY_SECRET
req_token_secret = DB_REQ_TOKEN_SECRET
req_token = DB_REQ_TOKEN
access_token = DB_ACCESS_TOKEN
access_token_secret = DB_ACCESS_TOKEN_SECRET

def encode_uri(s):
    return urllib2.quote(s, safe='~()*!.')

def sign_request(raw, key=None):
    from hashlib import sha1
    from hmac import new as hmac
    # If you dont have a token yet, the key should be only "CONSUMER_SECRET&"
    key = key or "%s&%s" % (consumer_secret, token_secret) 
    return "%s" % hmac(key, raw, sha1).digest().encode('base64')[:-1]

def gen_req_token():
    timestamp = str(int(time.mktime(datetime.now().timetuple())))
    nonce = base64.urlsafe_b64encode(''.join(random.sample(string.letters, 30)))
    post_data = {'oauth_consumer_key':api_key, 'oauth_signature_method':sign_method, 'oauth_timestamp':timestamp, 'oauth_nonce':nonce}
    post_data_sign = ['='.join((encode_uri(k), encode_uri(v))) for k,v in post_data.items()]
    post_data_sign.sort()
    post_data_sign = '&'.join(post_data_sign)
    post_data_sign = 'POST&%s&%s' % (encode_uri(douban_req_token_url), encode_uri(post_data_sign))
    print post_data_sign
    
    sign = sign_request(post_data_sign, '%s&' % api_key_secret)
    post_data['oauth_signature'] = sign
    print post_data
    
    post_data_str = '&'.join(['%s=%s' % (k, encode_uri(v)) for k,v in post_data.items()])
    print post_data_str

    print "curl --request 'POST' '%s' --data '%s' --verbose" % (douban_req_token_url, post_data_str)
    print 

#    req = urllib2.Request(douban_req_token_url, post_data_str)
#    response = urllib2.urlopen(req)

def gen_access_token():
    timestamp = str(int(time.mktime(datetime.now().timetuple())))
    nonce = base64.urlsafe_b64encode(''.join(random.sample(string.letters, 30)))
    post_data = {'oauth_consumer_key':api_key, 'oauth_signature_method':sign_method, 'oauth_timestamp':timestamp, 'oauth_nonce':nonce, 'oauth_token':req_token}
    post_data_sign = ['='.join((encode_uri(k), encode_uri(v))) for k,v in post_data.items()]
    post_data_sign.sort()
    post_data_sign = '&'.join(post_data_sign)
    post_data_sign = 'POST&%s&%s' % (encode_uri(douban_access_token_url), encode_uri(post_data_sign))
    print post_data_sign
    
    sign = sign_request(post_data_sign, '%s&%s' % (api_key_secret, req_token_secret))
    post_data['oauth_signature'] = sign
    print post_data
    
    post_data_str = '&'.join(['%s=%s' % (k, encode_uri(v)) for k,v in post_data.items()])
    print post_data_str

    print "curl --request 'POST' '%s' --data '%s' --verbose" % (douban_access_token_url, post_data_str)
    
def post2douban(content):
    entry = """<?xml version='1.0' encoding='UTF-8'?>
    <entry xmlns:ns0="http://www.w3.org/2005/Atom" xmlns:db="http://www.douban.com/xmlns/">
    <content>%s</content>
    </entry>""" % content
    timestamp = str(int(time.mktime(datetime.now().timetuple())))
    nonce = base64.urlsafe_b64encode(''.join(random.sample(string.letters, 30)))
    headers_data = {'oauth_consumer_key':api_key, 'oauth_signature_method':sign_method, 'oauth_timestamp':timestamp, 'oauth_nonce':nonce, 'oauth_token':access_token}
    
    headers_data_sign = ['='.join((encode_uri(k), encode_uri(v))) for k,v in headers_data.items()]
    headers_data_sign.sort()
    headers_data_sign = '&'.join(headers_data_sign)
    headers_data_sign = 'POST&%s&%s' % (encode_uri(douban_say_url), encode_uri(headers_data_sign))
    #print headers_data_sign
    
    sign = sign_request(headers_data_sign, '%s&%s' % (api_key_secret, access_token_secret))
    headers_data['oauth_signature'] = sign
    headers_data['realm'] = 'http://zhangchi.de/'
    #print headers_data
    
    headers_str = ', '.join(['%s="%s"' % (encode_uri(k), encode_uri(v)) for k, v in headers_data.items()])
    headers_str = 'OAuth %s' % headers_str
    header = {'Authorization': headers_str}
    
    header['Content-Type'] = 'application/atom+xml'
    #print header
    
    headers_str = ', '.join(['%s=%s' % (encode_uri(k), encode_uri(v)) for k, v in header.items()])

#    print "curl --request 'POST' '%s' --data '%s' --header '%s' --verbose" % (douban_say_url, post_data_str, headers_str)

    res = False
    try:
        conn = httplib.HTTPConnection("www.douban.com", 80)
        conn.request('POST', douban_say_url, entry, header)
        response = conn.getresponse().read()
        print response
        conn.close()
        res = True
        print 'Douban OK: %s' % content
    except:
        print 'Adding douban saying request error.'

    return res

if __name__ == '__main__':
    #gen_req_token()
    #gen_access_token()
    post2douban('test saying')
