# Team FiSci
# Hannah Ni, Hannah Walter, Lin Su

'''
This code scrapes words from Twitter and NYTimes.

Packages to install:
    - bs4 (beautiful soup)
    - urllib3
    - requests
    - regex
'''
import bs4
import urllib3
import requests
import re
import datetime as dt
import math
import time
import json
import urllib
import random
import collections
import matplotlib.pyplot as plt
#from fake_useragent import UserAgent

import opinion_words
import stock_scraper_v3
from imp import reload
reload(stock_scraper_v3)

pm = urllib3.PoolManager()

f = open('stop_words.txt', 'r')
stop_words = set(f.read().splitlines())
stop_words |= {'say', 'says', 'said', 'mr', 'like', 'likely', 'just', 
'including', 'way', 'going', 'dont', 'cant', 'company', 'companies', 
'percent'}

headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}

month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 
            'June': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

### SCRAPING SEEKING ALPHA WITH BEAUTIFUL SOUP ###

def scrape_sa(search_term, date, days):

    y = int(date[0:4])
    m = int(date[4:6])
    d = int(date[6:8])
    end_date_obj = dt.date(y, m, d)
    month_obj = dt.timedelta(days)
    begin_date_obj = end_date_obj - month_obj

    end_date = end_date_obj.isoformat()
    begin_date = begin_date_obj.isoformat()

    search_term = urllib.parse.quote_plus(search_term)

    url = "https://seekingalpha.com/symbol/AAPL/focus?page={}"
    base = "https://seekingalpha.com"
    page_count = 1

    url_dict = {}

    more_scrapes = True

    while more_scrapes:
        current_d = ''
        time.sleep(1)
        r = requests.get(url.format(str(page_count)), headers = headers)
        if r.status_code != 200:
            print(page_count, 'error')
        html = r.text
        soup = bs4.BeautifulSoup(html, 'lxml')
        items = soup.find_all('div', class_='symbol_article')

        for item in items:
            link = item.find_all('a')[0]['href']
            link = base + link
            date = item.find_all('div', class_='date_on_by')[0].text
            if 'Yesterday' in date:
                current_d = (dt.date.today() - dt.timedelta(1)).isoformat()
            date = re.findall('(?:(?:[A-Z][a-z]{2}, [A-Z][a-z]{2}\. [0-9]*)|(?:[A-Z][a-z]{2}\. [0-9]{1,2}, [0-9]{4}))', date)
            if len(date) > 0:
                date = date[0]
                date_m = month_dict[date[5:8]]
                date_d = date[-2:len(date)]
                if ' ' in date_d:
                    date_d = re.sub(' ' , '0', date_d)
                current_d = str(y) + '-' + date_m + '-' + date_d

                if current_d > end_date:
                    continue
                if current_d < begin_date:
                    more_scrapes = False
                    break
                else:
                    if current_d not in url_dict:
                        url_dict[current_d] = [link]
                    else:
                        url_dict[current_d].append(link)

        page_count += 1

    return url_dict

def scrape_urls(url_dict):
    article_dict = {}

    for date, url_list in url_dict.items():
        article_dict[date] = []
        for url in url_list:
            article = ''
            time.sleep(random.random)
            r = requests.get(url, headers = headers)
            if r.status_code != 200:
                print('error', url)
            html = r.text
            soup = bs4.BeautifulSoup(html, 'lxml')

            p_text_1 = soup.find_all('div', class_='p p1')
            p_text_2 = soup.find_all('p', class_='p p1')

            p_text = p_text_1 + p_text_2

            for p in p_text:
                article = article + p.text

            article_dict[date].append(article)

    return article_dict

### SCRAPING TWITTER THROUGH HTML ###

def html_search(search_term, date, days):
    headers = {'User-Agent': 'Mozilla/5.0'}

    search_term = urllib.parse.quote_plus(search_term)

    base_url = "https://twitter.com/search?f=tweets&vertical=default&q={}%20since%3A{}%20until%3A{}&src=typd"
    reload_url = "https://twitter.com/search?f=tweets&vertical=default&q={}%20since%3A{}%20until%3A{}&max_position={}&src=typd"

    y = int(date[0:4])
    m = int(date[4:6])
    d = int(date[6:8])
    end_date_obj = dt.date(y, m, d)
    month_obj = dt.timedelta(days)
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
            date = tweet.find_all('a', class_='tweet-timestamp js-permalink js-nav js-tooltip')[0]
            date_text = date['title'][-11:len(date['title'])]
            date_text = date_text[7:11] + '-' + month_dict[date_text[3:6]] + '-' + date_text[0:2]
            if date_text not in tweets_dict:
                tweets_dict[date_text] = [text.text]
            else:
                tweets_dict[date_text].append(text.text)

        pos = re.findall('data-max-position=\"(TWEET-[0-9]+-[0-9]+)', html)[0]

    return tweets_dict

def get_daily_twitter_sentiment(tweets_dict, search_term):
    search_term = re.sub('[^a-z0-9\-\']', '', search_term.lower())
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
                    or word[0] in ['$', '@'] or word == search_term):
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

### ANALYZING TWITTER SENTIMENT ###

def monte_carlo(sorted_daily_list, search_term):
    begin_date = sorted_daily_list[0][0]
    end_date = sorted_daily_list[-1][0]
    ticker = search_term[1:]

    stock_vals_df = stock_scraper_v3.historical_basic(ticker, begin_date, end_date, False)
    max_delta = max(abs(stock_vals_df['delta']))
    print(stock_vals_df)
    run_count = 10000
    current_run_count = 0
    current_sum_sq = None
    best_a = 0
    best_b = 0
    best_c = 0
    best_d = 0


    while current_run_count <= run_count:
        index_diff = 0

        A = random.uniform(0*max_delta, 200*max_delta)
        B = random.uniform(0*max_delta, 200*max_delta)
        C = random.uniform(0,1)
        D = random.uniform(0,1)

        sum_sq = 0
        model = 0
        initial_found = False

        for i, day in enumerate(sorted_daily_list):

            if day[0] not in stock_vals_df.index:
                index_diff += 1
                continue
            positive = float(day[1]['positive'])
            negative = float(day[1]['negative'])

            if not initial_found:
                model = stock_vals_df.loc[day[0], 'stock_val']
                intial_found = True

            val = A*(positive**C) - B*(negative**D)

            model += val

            #sq_error = (stock_vals_df.loc[day[0], 'delta'] - val)**2
            sq_error = (stock_vals_df.loc[day[0], 'stock_val'] - model)**2

            sum_sq += sq_error

        if current_sum_sq == None or current_sum_sq > sum_sq:
            current_sum_sq = sum_sq
            best_a = A
            best_b = B
            best_c = C
            best_d = D

        current_run_count += 1

    ax = plt.axes()
    ax.plot(range(len(stock_vals_df)), stock_vals_df['stock_val'])
    print(stock_vals_df['stock_val'])

    monte_carlo_sim = []
    current = 0

    initial_not_found = True
    index_diff = 0

    for i, day in enumerate(sorted_daily_list):
        print(i, day)
        if day[0] not in stock_vals_df.index:
            print('not in stock')
            continue
        if initial_not_found:
            print('initial value')
            monte_carlo_sim.append(stock_vals_df.loc[day[0], 'stock_val'])
            current = stock_vals_df.loc[day[0], 'stock_val']
            initial_not_found = False
            continue

        print('regular calculation')
        positive = float(day[1]['positive'])
        negative = float(day[1]['negative'])

        current += (positive**best_c)*best_a - (negative**best_d)*best_b
        monte_carlo_sim.append(current)

    ax.plot(range(len(stock_vals_df)), monte_carlo_sim)

    plt.show()

    print(monte_carlo_sim)

    return best_a, best_b, best_c, best_d

def plot(stock_vals, daily_list, best_a, best_b):
    
    ax = plt.axes()
    ax.plot(range(len(stock_vals)), stock_vals)

    monte_carlo_sim = [float(stock_vals[0])]
    current = float(stock_vals[0])

    for day in daily_list[1:]:
        positive = day[1]['positive']
        negative = day[1]['negative']

        val = current + float(positive*best_a - negative*best_b) 
        monte_carlo_sim.append(val)

    ax.plot(range(len(stock_vals)), monte_carlo_sim)

    plt.show()


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