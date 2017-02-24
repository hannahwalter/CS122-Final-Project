import bs4
import urllib3
import requests
import re
import datetime as dt
import math
import time
import json
import urllib

import oauth2

f = open('stop_words.txt', 'r')
stop_words = set(f.read().splitlines())
stop_words |= {'say', 'says', 'said', 'mr', 'like', 'likely', 'just', 
'including', 'way', 'going', 'dont', 'cant', 'company', 'companies', 
'percent'}

API_KEY = 'yIhvOOP5HLOj09upLo5PsOp1w'
API_SECRET = 'kN5ymLTkaESyX2EzvGEEQiyalumThykKdLLXbD3d70jfGwSMZM'

ACCESS_KEY = '733301270-Hg5n52rXSTpvwrfQAoLczgUI8jgwpAcllysVkAIU'
ACCESS_SECRET = 'eYShWymyKJPi2myY0E7hyPU9HdZz1y6MlrSDDyR5rhdpw'

URL = "https://api.twitter.com/1.1/search/tweets.json?q={}&count=100"

def get_tweet_list(search_term):

    search_term = urllib.parse.quote_plus(search_term)
    url = URL.format(search_term)

    consumer = oauth2.Consumer(key = API_KEY, secret = API_SECRET)
    token = oauth2.Token(key = ACCESS_KEY, secret = ACCESS_SECRET)
    client = oauth2.Client(consumer, token)
    resp, content = client.request(url)

    tweets_l = []
    data = json.loads(content.decode())
    tweets = data['statuses']

    for t in tweets:
        tweets_l.append(t['text'])

    return tweets_l

def parse_tweets(tweet_list, search_term):

    words_dict = {}

    for t in tweet_list:
        t_l = t.split()

        for word in t_l:
            word = re.sub('[^a-z0-9\-\']', '', word.lower())
            if (word in stop_words or word == '' or word == '-' 
                or word in search_term.lower() or word.isdigit()
                or word.startswith('http')):
                continue
            elif word not in words_dict:
                words_dict[word] = 1
            else:
                words_dict[word] += 1

    return words_dict

