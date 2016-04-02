# -*- coding: utf-8 -*-

from twython import Twython

from local_conf import *
post_twi_url = 'https://api.twitter.com/1.1/statuses/update.json'


def post2twi(status):
    twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, TOKEN, TOKEN_SECRET)
    twitter.update_status(status=status)
    return


if __name__ == '__main__':
    post2twi('Test tweet2')
