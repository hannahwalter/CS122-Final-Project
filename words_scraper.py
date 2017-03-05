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

# Getting opinion score
def get_opinion_score(search_item, date):
    positive, negative = opinion_words.get_word_lexicons()

    # NYT
    nyt_urls = get_search_urls(search_item, date)
    nyt_words = scrape_url_list(nyt_urls, search_item)

    p_score = 0
    n_score = 0

    for word, count in nyt_words.items():
        if word in positive:
            p_score += count
        elif word in negative:
            n_score += count
    
    return p_score, n_score

### SCRAPING TWITTER ###

test_twitter_url = "https://twitter.com/search?q=%23AAPL%20since%3A2017-03-01&src=typd"

# Using Selenium
def web_search(search_term):
    browser = webdriver.Chrome()
    browser.set_window_size(1120, 550)
    browser.get(test_twitter_url)

    last_height = browser.execute_script("return document.body.scrollHeight")
    
    more_scrolls = True

    while more_scrolls:
        print("more scrolls")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            more_scrolls = False
        else:
            last_height = new_height

    print(last_height)

    tweets = browser.find_elements_by_xpath("//p[@class='TweetTextSize  js-tweet-text tweet-text']")

    for tweet in tweets:
        print(tweet.text)

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

### USING NEW YORK TIMES API ###

def get_search_urls(search_item, date):
    '''
    INPUTS:
        search_item: string to search
        date: date as a string in format YYYYMMDD

    OUTPUTS:
        url_list: list of urls to articles from the past month,
            returned when item is searched
    ''' 
    y = int(date[0:4])
    m = int(date[4:6])
    d = int(date[6:8])
    end_date = dt.date(y, m, d)
    month = dt.timedelta(days=30)
    begin_date = end_date - month
    begin_date = begin_date.isoformat()
    begin_date = re.sub('-', '', begin_date)

    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?api-key=1175ef9507b5439ebd57ec8cc75b576d&q="
    s = search_item.lower()
    s = re.sub(' ', '+', s)

    url = url + s + '&begin_date=' + begin_date + '&end_date=' + date + '&sort=newest'

    r = requests.get(url)
    json = r.json()
    num_results = json['response']['meta']['hits']
    pages = math.ceil(num_results/10)

    url_list = []

    time.sleep(1)

    for i in range(pages):
        l = url + '&page=' + str(i)
        time.sleep(1)
        r = requests.get(l)
        json = r.json()
        search_results = json['response']['docs']
    
        for i in search_results:
            url_list.append(i['web_url'])

    return url_list

def scrape_url_list(url_list, search_item):
    '''
    INPUTS:
        url_list: list of urls to scrape
        search_item: string to search

    OUTPUTS:
        l: sorted list (in descending order) of all the words obtained from
        scraping the news sites and the associated count of words
    '''

    words_dict = {}

    for url in url_list:
        r = requests.get(url)
        if not r.status_code == requests.codes.ok:
            continue
        html = r.text
        soup = bs4.BeautifulSoup(html, 'lxml')

        story_text = soup.find_all('p', class_ = 'story-body-text story-content')

        for paragraph in story_text:
            text = paragraph.text
            text_l = text.split()

            for word in text_l:
                word = re.sub('[^a-z0-9\-\']', '', word.lower())
                if (word in stop_words or word == '' or word == '-' 
                    or word in search_item.lower() or word.isdigit()):
                    continue
                elif word not in words_dict:
                    words_dict[word] = 1
                else:
                    words_dict[word] += 1

    l = sorted(words_dict.items(), key = lambda x: x[1], reverse = True)
    return words_dict