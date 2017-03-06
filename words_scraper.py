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
import random

pm = urllib3.PoolManager()

f = open('stop_words.txt', 'r')
stop_words = set(f.read().splitlines())
stop_words |= {'say', 'says', 'said', 'mr', 'like', 'likely', 'just', 
'including', 'way', 'going', 'dont', 'cant', 'company', 'companies', 
'percent'}

<<<<<<< HEAD
### SCRAPING TWITTER THROUGH HTML ###

def html_search(search_term, date):
    headers = {'User-Agent': 'Mozilla/5.0'}

    search_term = urllib.parse.quote_plus(search_term)

    base_url = "https://twitter.com/search?f=tweets&vertical=default&q={}%20since%3A{}%20until%3A{}&src=typd"
    reload_url = "https://twitter.com/search?f=tweets&vertical=default&q={}%20since%3A{}%20until%3A{}&max_position={}&src=typd"

    y = int(date[0:4])
    m = int(date[4:6])
    d = int(date[6:8])
    end_date_obj = dt.date(y, m, d)
    month_obj = dt.timedelta(days=30)
    begin_date_obj = end_date_obj - month_obj

    end_date = end_date_obj.isoformat()
    begin_date = begin_date_obj.isoformat()

    tweets_dict = {}

    initial_run = True

    while True:
        time.sleep(random.random())
        if initial_run:
            r = requests.get(base_url.format(search_term, begin_date, end_date), headers = headers)
            initial_run = False
        else:
            r = requests.get(reload_url.format(search_term, begin_date, end_date, pos), headers = headers)

        html = r.text
        soup = bs4.BeautifulSoup(html, 'lxml')
        tweets = soup.find_all('li', class_='js-stream-item stream-item stream-item ')

        if tweets == []:
            break

        for tweet in tweets:
            text = tweet.find_all('p', class_=re.compile('TweetTextSize js-tweet-text tweet-text*'))[0]
            date = tweet.find_all('span', class_='_timestamp js-short-timestamp ')[0]
            if date.text not in tweets_dict:
                tweets_dict[date.text] = [text.text]
            else:
                tweets_dict[date.text].append(text.text)

        pos = re.findall('data-max-position=\"(TWEET-[0-9]+-[0-9]+)', html)[0]

    return tweets_dict

def get_daily_twitter_sentiment(tweets_dict, search_term):
    positive, negative = opinion_words.get_word_lexicons()

    daily_dict = {}
    total_dict = {}

    for key, val in tweets_dict.items():
        daily_dict[key] = {'positive': 0, 'negative': 0}
        for tweet in val:
            tweet_l = tweet.split()
            for word in tweet_l:
                word = re.sub('[^a-z0-9\-\']', '', word.lower())
                if (word in stop_words or word == '' or word == '-' 
                    or word.isdigit() or 'twittercom' in word or 'http' in word
                    or word[0] in ['$', '@'] or word in search_term):
                    continue
                else:
                    if word in positive:
                        daily_dict[key]['positive'] += 1
                    elif word in negative:
                        daily_dict[key]['negative'] += 1

                    if word not in total_dict:
                        total_dict[word] = 1
                    else:
                        total_dict[word] += 1

    sorted_words = sorted(total_dict.items(), key = lambda x: x[1], reverse = True)
    sorted_daily_list = sorted(daily_dict.items())

    return sorted_daily_list, sorted_words

### GETTING PERCENTAGES FROM TWITTER ###

def get_percentages(sorted_daily_list):
    y_vals = []
    x_vals = []
    negative_l = []
    positive_l = []
    current = 0

    for item in sorted_daily_list:
        negative = item[1]['negative']
        positive = item[1]['positive']
        total = negative + positive

        positive_l.append(positive/total)
        negative_l.append(negative/total)

        if negative > positive:
            ratio = (positive-negative)/total
        elif positive > negative:
            ratio = (positive-negative)/total
        else:
            ratio = 0

        current += ratio

        y_vals.append(current)
        x_vals.append(item[0])

    return x_vals, y_vals, positive_l, negative_l

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

### NYT GET OPINION SCORE ###

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