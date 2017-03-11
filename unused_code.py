import bs4
import urllib3
import requests
import re
import datetime as dt
import math
import time
import json
import urllib
import opinion_words
import oauth2
import random
import lxml.html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

pm = urllib3.PoolManager()

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

# Trying to login to seeking alpha
def test_sa():
    login = "https://seekingalpha.com/account/login"
    s = requests.session()
    login_page = s.get(login, headers = headers)

    soup = bs4.BeautifulSoup(login_page.text, 'lxml')
    inputs = soup.find_all('input', attrs = {'name': True})

    form = {}

    for i in inputs:
        if not i.has_attr('value'):
            form[i['name']] = ''
        else:
            form[i['name']] = i['value']

    form['user[email]'] = 'hannahni@uchicago.edu'
    form['user[password]'] = 'deanboyer'

    response = s.post(login, data = form, headers = headers)
    sa_text = response.text
    soup = bs4.BeautifulSoup(sa_text, 'lxml')

    title = soup.find_all('div', class_='title_tab')

    print(title)
# Using Selenium to scrape Twitter
def selenium_search(search_term, date):

    search_term = urllib.parse.quote_plus(search_term)
    url = "https://twitter.com/search?q={}%20since%3A{}%20until%3A{}&src=typd"

    y = int(date[0:4])
    m = int(date[4:6])
    d = int(date[6:8])
    end_date = dt.date(y, m, d)
    fortnight = dt.timedelta(days=15)
    mid_date = (end_date - fortnight).isoformat()
    begin_date = (end_date - fortnight -fortnight).isoformat()

    search_url_1 = url.format(search_term, begin_date, mid_date)
    search_url_2 = url.format(search_term, mid_date, end_date) 

    browser = webdriver.Chrome()
    browser.get(search_url_1)

    last_height = browser.execute_script("return document.body.scrollHeight")
    
    more_scrolls = True

    while more_scrolls:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            more_scrolls = False
        else:
            last_height = new_height

    tweets = browser.find_elements_by_xpath("//p[@class='TweetTextSize  js-tweet-text tweet-text']")
    tweet_list = []
    for tweet in tweets:
        tweet_list.append(tweet.text)

    return tweet_list

# Using the Twitter API

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