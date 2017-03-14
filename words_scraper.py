'''
TEAM: FiSci
PEOPLE: Hannah Ni, Hannah Walter, Lin Su

This file scrapes words from Twitter, NYTimes, and Selenium.
'''

import bs4
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

import util as u
import stock_scraper

STOP_WORDS = u.get_stop_words()
POSITIVE, NEGATIVE = u.get_word_lexicons()

HEADER = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}

MONTH_DICT = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 
            'June': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 
            'Nov': '11', 'Dec': '12'}

### SCRAPING SEEKING ALPHA ###

def get_sa_urls(ticker, begin_date, end_date):

    reload_url = "https://seekingalpha.com/symbol/" + ticker + "/focus?page={}"
    base = "https://seekingalpha.com"
    page_count = 1
    url_list = []
    more_pages = True
    inaccessible = 0

    while more_pages:
        time.sleep(random.random())
        current_d = ''

        r = requests.get(reload_url.format(str(page_count)), headers = HEADER)
        if r.status_code != 200:
            inaccessible += 1
        html = r.text
        soup = bs4.BeautifulSoup(html, 'lxml')
        search_items = soup.find_all('div', class_='symbol_article')

        for item in search_items:
            if 'symbol_pro_research' in str(item):
                continue

            link = item.find_all('a')[0]['href']
            link = base + link

            # Determining the date of the article
            date = item.find_all('div', class_='date_on_by')[0].text
            if 'Yesterday' in date:
                current_d = (dt.date.today() - dt.timedelta(1)).isoformat()
            elif 'Today' in date:
                current_d = (dt.date.today()).isoformat()
            else:
                raw_date = re.findall('(?:(?:[A-Z][a-z]{2}, [A-Z][a-z]{2}\. '
                    '[0-9]*)|(?:[A-Z][a-z]{2}\. [0-9]{1,2}, [0-9]{4}))', date)
                if raw_date == []:
                    return False
                elif len(raw_date) > 0:
                    date = raw_date[0]
                    # Determining format of date: 'Wed, Mar. 8' or 'Mar. 8, 2016'
                    if not re.search(r'[0-9]{4}', date):
                        date_m = MONTH_DICT[date[5:8]]
                        date_d = date[-2:len(date)]
                        if ' ' in date_d:
                            date_d = re.sub(' ' , '0', date_d)
                        current_d = (str(dt.datetime.now().year) + '-' + date_m 
                                    + '-' + date_d)
                    else:
                        current_d = (dt.datetime.strptime(date, '%b. %d, %Y').date()
                                    .isoformat())

            if current_d > end_date:
                continue
            elif current_d < begin_date:
                more_pages = False
                break
            else:
                url_list.append(link)

        page_count += 1

    if len(url_list) == 0:
        return "No articles could be found or accessed for this company."
    else:
        return url_list, inaccessible

def scrape_sa_urls(url_list):

    article_list = []
    inaccessible = 0

    for url in url_list:
        time.sleep(1)
        article = ''

        r = requests.get(url, headers = HEADER)
        if r.status_code != 200:
            inaccessible += 1
        html = r.text
        soup = bs4.BeautifulSoup(html, 'lxml')

        summary = soup.find_all('div', class_='article-summary article-width')
        p_text = soup.find_all('div', class_='sa-art article-width')
        article_text = summary + p_text
        article_text = [x.text for x in article_text]

        article = ' '.join(article_text)

        article_list.append(article)

    return article_list, inaccessible

### SCRAPING TWITTER ###

def get_tweets(ticker, begin_date, end_date):

    search_term = urllib.parse.quote_plus('#' + ticker)

    base_url = ("https://twitter.com/search?f=tweets&vertical=default&q={}"
                "%20since%3A{}%20until%3A{}&src=typd")
    reload_url = ("https://twitter.com/search?f=tweets&vertical=default&q={}"
                "%20since%3A{}%20until%3A{}&max_position={}&src=typd")

    tweets_dict = {}
    initial_run = True

    while True:
        time.sleep(random.uniform(.5,1))

        if initial_run:
            r = requests.get(base_url.format(search_term, 
                begin_date, end_date), headers = HEADER)
            initial_run = False
        else:
            r = requests.get(reload_url.format(search_term,
                begin_date, end_date, pos), headers = HEADER)

        html = r.text
        soup = bs4.BeautifulSoup(html, 'lxml')
        tweets = soup.find_all('li', class_='js-stream-item stream-item '
            'stream-item ')

        if tweets == []:
            break

        for tweet in tweets:
            text = tweet.find_all('p', class_=re.compile('TweetTextSize '
                'js-tweet-text tweet-text*'))[0]
            date = tweet.find_all('a', class_='tweet-timestamp js-permalink '
                'js-nav js-tooltip')[0]

            date_text = re.findall('[0-9]+ [A-Z][a-z]+ [0-9]{4}', str(date))[0]
            date_iso = dt.datetime.strptime(date_text, '%d %b %Y').date().isoformat()
  
            if date_iso not in tweets_dict:
                tweets_dict[date_iso] = [text.text]
            else:
                tweets_dict[date_iso].append(text.text)

        pos = re.findall('data-max-position=\"(TWEET-[0-9]+-[0-9]+)', html)[0]

    return tweets_dict

def get_twitter_words(tweets_dict, ticker):
    ticker = ticker.lower()

    daily_dict = {}
    total_dict = {}

    for key, val in tweets_dict.items():
        daily_dict[key] = {'positive': 0, 'negative': 0}
        for tweet in val:
            tweet_l = tweet.split()
            for word in tweet_l:
                word = re.sub('[^a-z0-9\-\']', '', word.lower())
                if (word in STOP_WORDS or word == '' or word == '-' 
                    or word.isdigit() or 'twittercom' in word or 'http' in word
                    or word == ticker):
                    continue
                else:
                    if word in POSITIVE:
                        daily_dict[key]['positive'] += 1
                    elif word in NEGATIVE:
                        daily_dict[key]['negative'] += 1

                    if word not in total_dict:
                        total_dict[word] = 1
                    else:
                        total_dict[word] += 1

    sorted_words = sorted(total_dict.items(), key = lambda x: x[1], 
                    reverse = True)
    sorted_daily_list = sorted(daily_dict.items())

    return sorted_daily_list, sorted_words

### ANALYZING TWITTER SENTIMENT ###

def monte_carlo(sorted_daily_list, ticker, run_count):
    begin_date = sorted_daily_list[0][0]
    end_date = sorted_daily_list[-1][0]

    stock_vals_df = stock_scraper.historical_basic(ticker, begin_date, end_date, False)
    max_delta = max(abs(stock_vals_df['delta']))

    current_run_count = 0
    current_sum_sq = None
    best_a = 0
    best_b = 0
    best_c = 0
    best_d = 0
    initial_found = False

    while current_run_count <= run_count:

        A = random.uniform(0, 10*max_delta)
        B = random.uniform(0, 10*max_delta)
        C = random.uniform(0,1)
        D = random.uniform(0,1)

        #A = random.uniform(0, 10*max_delta)
        #B = random.uniform(0, 10*max_delta)
        #C = random.uniform(0,1)
        #D = random.uniform(0,1)

        sum_sq = 0
        model = 0

        for i, day in enumerate(sorted_daily_list[1:]):

            if day[0] not in stock_vals_df.index:
                continue
            positive = float(day[1]['positive'])
            negative = float(day[1]['negative'])

            if not initial_found:
                model = stock_vals_df.loc[day[0], 'stock_val']
                intial_found = True

            val = A*(positive**C) - B*(negative**D)
            model += val

            #sq_error = (abs(stock_vals_df.loc[day[0], 'delta']) - abs(val))**2
            sq_error = (stock_vals_df.loc[day[0], 'stock_val'] - model)**2

            sum_sq += sq_error

        if current_sum_sq == None or current_sum_sq > sum_sq:
            current_sum_sq = sum_sq
            best_a = A
            best_b = B
            best_c = C
            best_d = D

        current_run_count += 1

    monte_carlo_sim = plot(stock_vals_df, sorted_daily_list, best_a, best_b, best_c, best_d)

    dates_list = stock_vals_df['date'].tolist()
    stock_vals = [round(x, 2) for x in stock_vals_df['stock_val'].tolist()]

    return dates_list, monte_carlo_sim, stock_vals


def plot(stock_vals_df, sorted_daily_list, best_a, best_b, best_c, best_d):

    plt.plot(stock_vals_df['stock_val'])

    monte_carlo_sim = []
    current = 0
    initial_found = False

    for i, day in enumerate(sorted_daily_list):
        if day[0] not in stock_vals_df.index:
            continue
        if not initial_found:
            monte_carlo_sim.append(stock_vals_df.loc[day[0], 'stock_val'])
            current = stock_vals_df.loc[day[0], 'stock_val']
            initial_found = True
            continue

        positive = float(day[1]['positive'])
        negative = float(day[1]['negative'])

        current += (positive**best_c)*best_a - (negative**best_d)*best_b
        monte_carlo_sim.append(current)

    plt.plot(monte_carlo_sim)

    plt.ylabel('stock value\nactual values vs. simulated values')

    plt.xlabel('dates')
    
    plt.savefig('static/twitter.png')

    plt.clf()

    return [round(x, 2) for x in monte_carlo_sim]

### SCRAPING NEW YORK TIMES ###

def get_nyt_urls(search_item, beginning_date, ending_date):
    '''
    INPUTS:
        search_item: string to search
        date: date as a string in format YYYYMMDD

    OUTPUTS:
        url_list: list of urls to articles from the past month,
            returned when item is searched
    ''' 
    
    end_date = re.sub('-', '', ending_date)
    begin_date = re.sub('-', '', beginning_date)

    url = ("https://api.nytimes.com/svc/search/v2/articlesearch.json?api-key"
        "=1175ef9507b5439ebd57ec8cc75b576d&q=")
    s = re.sub(' ', '+', search_item.lower())

    url += (s + '&begin_date=' + begin_date + '&end_date=' + end_date 
            + '&sort=newest')

    r = requests.get(url, headers = HEADER)
    json = r.json()
    num_results = json['response']['meta']['hits']
    if num_results == 0:
        return "No results available"
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

def scrape_nyt_urls(url_list, search_item):
    '''
    INPUTS:
        url_list: list of urls to scrape
        search_item: string to search
        naive_bayes: Boolean

    OUTPUTS:
        l: sorted list (in descending order) of all the words obtained from
        scraping the news sites and the associated count of words
    '''

    words_dict = {}
    articles = []
    inaccessible = 0

    for url in url_list:

        r = requests.get(url, headers = HEADER)
        if r.status_code != 200:
            inaccessible += 1
        html = r.text
        soup = bs4.BeautifulSoup(html, 'lxml')

        story_text = soup.find_all('p', class_ = 'story-body-text story-content')
        story_text = [x.text for x in story_text]
            
        article = ' '.join(story_text)
        
        articles.append(article)

    return articles, inaccessible

### GENERAL FUNCTIONS ###

def bag_of_words_score(words_list):

    p_score = 0
    n_score = 0

    for word, count in words_list:
        if word in POSITIVE:
            p_score += count
        elif word in NEGATIVE:
            n_score += count

    p_percentage = round((p_score / (p_score + n_score)) * 100, 2)
    n_percentage = round((n_score / (p_score + n_score)) * 100, 2)
    
    return p_percentage, n_percentage

def split_strings_into_list(strings_list, search_item):

    words_dict = {}

    for string in strings_list:
        string_l = string.split()

        for word in string_l:
            word = re.sub('[^a-z0-9\-\']', '', word.lower())
            if (word in STOP_WORDS or word == '' or word == '-' 
                or word == search_item.lower() or word.isdigit()):
                continue
            elif word not in words_dict:
                words_dict[word] = 1
            else:
                words_dict[word] += 1
    
    sorted_words = sorted(words_dict.items(), key = lambda x: x[1], 
        reverse = True)

    return sorted_words



