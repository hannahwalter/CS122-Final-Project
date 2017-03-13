# Team FiSci
# Hannah Ni, Hannah Walter, Lin Su

'''
This code collects historical and real-time data on stocks
from Yahoo finance API.

Packages to install:
    yahoo-finance
'''

from yahoo_finance import Share
import math
import datetime as dt
import quandl
import numpy as np
import pandas as pd

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from json import loads
import re

quandl.ApiConfig.api_key = 'DZFGSrUkQDFyReYx1gvx'

def find_ticker_and_name(company_input):
    df = pd.DataFrame(pd.read_csv('files_for_code/companylist.csv'))
    df_by_ticker_match = df[df['Symbol'] == company_input.upper()]
    if len(df_by_ticker_match) == 1:
        ticker = df_by_ticker_match['Symbol'].tolist()[0]
        name = df_by_ticker_match['Name'].tolist()[0]
        return ticker, name
    else:
        df_by_name_match = df[df['Name'].str.contains(company_input.upper(), case=False)]
        symbols = df_by_name_match['Symbol'].tolist()
        names = df_by_name_match['Name'].tolist()
        if len(symbols) == 0:
            return "No matches were found. Please check your spelling and try again."
        elif len(symbols) == 1:
            return symbols[0], names[0]
        else:
            matches_string = ("We found the following tickers and companies "
                "that contain your input. ")
            tuples = zip(symbols, names)
            for i, val in enumerate(tuples):
                matches_string += str(i+1) + '. ' + val[0] + ', ' + val[1] + ' '
            matches_string += "Please try again with the correct spelling."
            return matches_string

def historical_basic(ticker, start_date, end_date, only_start_and_end):
    '''
    Inputs:
        ticker: company ticker, string
        start_date: 'yyyy-mm-dd'
        end_date: 'yyyy-mm-dd'
        only_start_and_end: a Boolean.
            False will return information for all days in between start_date and end_date
            True will return information only for the start_date and end_date if both dates are business days
                If start_date or end_date is not business day,
                    will return information for the closest date after or before the specified date
    '''

    raw = Share(ticker).get_historical(start_date, end_date)
    raw = raw[::-1]

    processed = {'date': [], 'stock_val': [], 'delta': []}
    deltas = []
    for i, day_data in enumerate(raw):
        if i == 0:
            processed['delta'].append(0)
        else:
            processed['delta'].append(float(raw[i-1]['Close']) - float(day_data['Close']))
        processed['date'].append(day_data['Date'])
        processed['stock_val'].append(float(day_data['Close']))

    processed_df = pd.DataFrame(processed)
    processed_df = processed_df.set_index(['date'], drop = False)

    return processed_df