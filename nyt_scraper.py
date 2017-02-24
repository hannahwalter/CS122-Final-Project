import bs4
import urllib3
import requests
import re
import datetime as dt
import math
import time

pm = urllib3.PoolManager()

f = open('stop_words.txt', 'r')
stop_words = set(f.read().splitlines())
stop_words |= {'say', 'says', 'said', 'mr', 'like', 'likely', 'just', 
'including', 'way', 'going', 'dont', 'cant', 'company', 'companies', 
'percent'}

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

    time.sleep(.5)

    for i in range(pages):
        l = url + '&page=' + str(i)
        time.sleep(1)
        r = requests.get(l)
        r.raise_for_status()
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
        soup = bs4.BeautifulSoup(html)

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
    return l
