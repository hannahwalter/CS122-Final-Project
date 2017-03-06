# Copyright FiSci, 2017, all rights reserved
# A Lin Su production

'''
To collect historical and real-time data on stocks
from Yahoo finance and Quandl via API
to test strategy and provide information to make decision
'''



'''
Before running this file, please intall Yahoo finance on your machine:
1. Open https://pypi.python.org/pypi/yahoo-finance in your browser
2. Search for yahoo-finance-1.4.0.tar.gz on this page
3. Download the installation package
4. Navigate to the download folder in command line
5. Run the command: $ sudo python setup.py install
6. Replace the file yql.py in the folder yahoo-finance-1.4.0 with the attached updated file (there are some bugs in the downloaded package and I fixed them)
7. Run this file in iPython
'''

'''
If further information about company or stock is needed (e.g. auditor information, revenue on 10-K),
please do not hesitate to tell me (Lin Su), as we have more resources on Quandl API to extract.
'''

from yahoo_finance import Share
import math
import quandl
quandl.ApiConfig.api_key = 'DZFGSrUkQDFyReYx1gvx'
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from json import loads



'''
Convert user input to ticker for later use.
User will be guided to enter company name or ticker in the command line when running this file.
'''
ticker = ''
while ticker == '':
    while True:
        company_input = str(input("Please enter a company name or ticker: "))
        response = urlopen('http://chstocksearch.herokuapp.com/api/{}'.format(company_input))
        string = response.read().decode('utf-8')
        json_obj = loads(string)
        if len(json_obj) == 1:
            print("Sorry, we could not find any company name or ticker that contains your input.\nPlease check your spelling and try again: ")
            continue
        else:
            break
    if len(json_obj) == 2: 
        ticker = json_obj[0]['symbol']
    else:
        print('We found the following company names and tickers that contain your input: ')
        for index, company in enumerate(json_obj[:-1]):
            print(index + 1, company)
        while True:
            select = input('If none of the above companies is what you intended to search, please enter anything but an integer. Otherwise, please enter its index: ')
            try:
                index = int(select)
                if index > 0 and index < len(json_obj):
                    ticker = json_obj[index - 1]['symbol']
                    break
                else:
                    print('Sorry, index out of range, please try again: ')
                    continue
            except ValueError:
                print('Sorry, we could not recognize the index that you entered just now.\n\nPlease try again from the start: ')
                break





def historical_basic(start_date, end_date, only_start_and_end):
    '''
    Inputs:
        start_date: 'yyyy-mm-dd'
        end_date: 'yyyy-mm-dd'
        only_start_and_end: a Boolean.
            False will return information for all days in between start_date and end_date
            True will return information only for the start_date and end_date if both dates are business days
                If start_date or end_date is not business day,
                    will return information for the closest date after or before the specified date
    '''
    raw = Share(ticker).get_historical(start_date, end_date)
    if only_start_and_end:
        return_rate_per_day = math.pow(( float(raw[0]['High']) / float(raw[-1]['Low']) ), (1/(len(raw)-1))) - 1
        return return_rate_per_day
    else:
        processed = []
        for day_data in raw:
            processed.append(day_data['Close'])
        return processed



def find_date_range_start(approximate_date, range_of_approximation):
    '''
    Helper function for historical_optimized
    '''
    assert range_of_approximation <= 28, 'tolerance of approximation should be smaller than 29'

    day = int(approximate_date[8:])
    month = int(approximate_date[5:7])
    year = int(approximate_date[:4])

    day -= range_of_approximation
    if day < 1:
        month -= 1
        if month < 1:
            year -= 1
            month += 12
        if month == 4 or month == 6 or month == 9 or month == 11:
            day += 30
        elif month == 2:
            if year % 4 == 0 and year % 400 != 0:
                day += 29
            else:
                day += 28
        else:
            day += 31

    start_date = str(year) + '-' + str(month) + '-' + str(day)
    return start_date

def find_date_range_end(approximate_date, range_of_approximation):
    '''
    Helper funcion for historical_optimized
    '''
    assert range_of_approximation <= 28, 'tolerance of approximation should be smaller than 29'

    day = int(approximate_date[8:])
    month = int(approximate_date[5:7])
    year = int(approximate_date[:4])
    day += range_of_approximation
    if month == 4 or month == 6 or month == 9 or month == 11:
        if day > 30:
            month += 1
            day -= 30
    elif month == 2:
        if year % 4 == 0 and year % 400 != 0:
            if day > 29:
                month += 1
                day -= 29
        else:
            if day > 28:
                month += 1
                day -= 28
    else:
        if day > 31:
            month += 1
            day -= 31
    if month > 12:
        year += 1
        month -= 12

    end_date = str(year) + '-' + str(month) + '-' + str(day)
    return end_date



def historical_optimized(approximate_start_date, approximate_end_date, range_of_approximation):
    '''
    Accoridng to our sentiment analysis, there may be a window of more than one day to buy or sell.
    This function helps optimize the buy and sell date around an approximate date, so that return on investment
    is maximized.
    Input:
        approximate_start_date: a string of the form 'yyyy-mm-dd'
        approximate_end_date: a string of the form 'yyyy-mm-dd'
        range_of_approximation: an integer representing how many days before or after the approximation is allowed.
    Output:
        a tuple of (return rate per day, [optimized date to sell, optimized date to buy])
    '''
    start_start = find_date_range_start(approximate_start_date, range_of_approximation)
    end_start = find_date_range_end(approximate_start_date, range_of_approximation)
    start_end = find_date_range_start(approximate_end_date, range_of_approximation)
    end_end = find_date_range_end(approximate_end_date, range_of_approximation)

    start_raw = Share(ticker).get_historical(start_start, end_start)
    start_min = float(start_raw[0]['Low'])
    for day_data in start_raw:
        if float(day_data['Low']) < start_min:
            start_min = float(day_data['Low'])
            start_min_date = day_data['Date']

    end_raw = Share(ticker).get_historical(start_end, end_end)
    end_max = float(end_raw[0]['High'])
    for day_data in end_raw:
        if float(day_data['High']) > end_max:
            end_max = float(day_data['High'])
            end_max_date = day_data['Date']

    business_days = len(Share(ticker).get_historical(start_min_date, end_max_date))

    return_rate_per_day = math.pow(( end_max / start_min ), (1/(business_days-1))) - 1

    return return_rate_per_day, [end_max_date, start_min_date]