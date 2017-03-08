import bs4
import urllib3
import requests
import re
import datetime as dt
import math
import time
import json
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

SCROLL_TO = 250

def get_search_urls(search_term):

    url = "http://seekingalpha.com/symbol/"+ search_term+"/focus"
    browser = webdriver.Chrome()
    browser.get(url)

    scroll_script = "window.scrollTo(0," + SCROLL_TO + ")" 
    browser.execute_script(scroll_script)
    articles = browser.find_elements(By.CLASS_NAME, "symbol_article")
    
    url_list = []

    for article in articles:
        new_url = article.get_attribute("href")
        url_list.append(new_url)

    return url_list








