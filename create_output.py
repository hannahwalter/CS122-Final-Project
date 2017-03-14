'''
TEAM: FiSci
PEOPLE: Hannah Ni, Hannah Walter, Lin Su

This file provides aggregates our functions into a Django-compatible format.
'''

import datetime as dt
import words_scraper
import stock_scraper
import naive_bayes
import svm
import util

from imp import reload
reload(stock_scraper)
reload(words_scraper)

def create_output(args):
    '''
    Master function to aggregate all our code into the appropriate 
    output format.

    INPUTS:
        args: dictionary with the following keys:
            company_name: name of company
            date: date to scrape up until
            days: number of days to scrape for before date
            bag_of_words, monte_carlo, advanced_sentiment: Boolean, if this analysis 
                is desired
    OUTPUTS:
        dictionary of lists with the desired data to be formatted for Django
    '''

    output_dict = {}

    name = args['company_name']
    date = args['date']
    days = args['days']

    if date > dt.date.today().isoformat():
        output_dict['date_error'] = (['Please enter a date before today' 
            ' and try again.'])
        return output_dict
    elif date < (dt.date.today() - dt.timedelta(365)).isoformat():
        output_dict['date_error'] = (['Please enter a date less than a year' 
            ' ago and try again.'])
        return output_dict

    # Generating appropriate isoformat dates
    end_date_obj = dt.datetime.strptime(date, '%Y-%m-%d').date()
    delta_obj = dt.timedelta(days)
    begin_date_obj = end_date_obj - delta_obj

    end_date = date
    begin_date = begin_date_obj.isoformat()

    # Finding company ticker
    find_ticker_company = stock_scraper.find_ticker_and_name(name)
    if len(find_ticker_company) != 2:
        output_dict['input_error'] = [find_ticker_company]
        return output_dict
    else:
        ticker = find_ticker_company[0]
        company_name = find_ticker_company[1]

    nyt_continue = True
    sa_continue = True

    nyt_inaccessible = 0
    sa_articles_inaccessible = 0
    sa_scrape_inaccessible = 0

    if args['bag_of_words'] or args['monte_carlo']:
        output_dict['bag_of_words'] = [[''], ['positive words'], ['negative words'], ['recommendation']]
        output_dict['top_words'] = ([[''], ['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7'], ['8'],
            ['9'], ['10']])
        tweets = words_scraper.get_tweets(ticker, begin_date, end_date)
        daily_words_list, total_words_list = (words_scraper
            .get_twitter_words(tweets, ticker))
        
        t_top_words = total_words_list[0:10]

        for i, word in enumerate(t_top_words):
            output_dict['top_words'][i+1].append(word[0])

        t_percentage_tuple = (words_scraper.
            bag_of_words_score(total_words_list))
        if type(t_percentage_tuple) == str:
            output_dict['bag_of_words_error'] = (['There was not enough data to' 
                ' retrieve bag of words percentages for Twitter. Please try again.'])
        else:
            t_p_percentage = t_percentage_tuple[0]
            t_n_percentage = t_percentage_tuple[1]

            output_dict['bag_of_words'][0].append('Twitter')
            output_dict['top_words'][0].append('Twitter')

            t_recommendation = util.recommendation(t_p_percentage, 
                t_n_percentage)

            output_dict['bag_of_words'][1].append(t_p_percentage)
            output_dict['bag_of_words'][2].append(t_n_percentage)
            output_dict['bag_of_words'][3].append(t_recommendation)
        
    if args['bag_of_words'] or args['advanced_sentiment']:
        nyt_urls = words_scraper.get_nyt_urls(company_name, begin_date, end_date)
        if type(nyt_urls) == str:
            output_dict['bag_of_words_error'] = [nyt_urls]
            nyt_continue = False
        else:
            nyt_articles_list, nyt_inaccessible = (words_scraper.
                scrape_nyt_urls(nyt_urls, company_name))

        sa_urls = words_scraper.get_sa_urls(ticker, begin_date, end_date)
        if type(sa_urls) == str:
            output_dict['bag_of_words_error'] = [sa_urls]
            sa_continue = False
        else:
            sa_scrape_inaccessible = sa_urls[1]
            sa_articles_list, sa_articles_inaccessible = words_scraper.scrape_sa_urls(sa_urls[0])

    if args['bag_of_words']:
        if nyt_continue:
            output_dict = bow_format(nyt_articles_list, company_name, output_dict, 'New York Times')

        if sa_continue:
            output_dict = bow_format(sa_articles_list, company_name, output_dict, 'Seeking Alpha')

        output_dict['inaccessible_count'] = [(sa_scrape_inaccessible + sa_articles_inaccessible 
            + nyt_inaccessible)]

    if args['monte_carlo']:
        dates, monte_carlo, stock = words_scraper.monte_carlo(daily_words_list, ticker, 5000)
        output_dict['monte_carlo'] = [['dates'] + dates, ['monte carlo'] + monte_carlo, ['stock'] + stock]

    if args['advanced_sentiment'] and (nyt_continue or sa_continue):

        adv_list = []
        if nyt_continue:
            adv_list.extend([['NYTIMES', '', '', '']])
            adv_nyt_list = svm.final_output(50, 50, nyt_articles_list)
            adv_list.extend(adv_nyt_list)
            
        if sa_continue:
            adv_list.extend([['-', '-', '-', '-'], ['SEEKING ALPHA', '', '', '']])
            adv_sa_list = svm.final_output(50, 50, sa_articles_list)
            adv_list.extend(adv_sa_list)

        output_dict['advanced_sentiment'] = adv_list
 
    return output_dict

def bow_format(articles_list, company_name, output_dict, source):
    '''
    Function to handle repeated formatting procedure for Seeking Alpha and NYTimes.

    INPUTS:
        articles_list: list of articles
        company_name: name of the company
        output_dict: current output dictionary
        source: Seeking Alpha or New York Times
    OUTPUTS:
        updated output dict
    '''

    words_list = words_scraper.split_strings_into_list(articles_list, company_name)
    percentage_tuple = words_scraper.bag_of_words_score(words_list)
    if type(percentage_tuple) == str:
        output_dict['bag_of_words_error'] = (['There was not enough data to' 
            ' retrieve bag of words percentages for '  + source + '. Please try again.'])
    else:
        p_percentage = percentage_tuple[0]
        n_percentage = percentage_tuple[1]
        recommendation = util.recommendation(p_percentage, n_percentage)

        output_dict['bag_of_words'][0].append(source)
        output_dict['bag_of_words'][1].append(p_percentage)
        output_dict['bag_of_words'][2].append(n_percentage)
        output_dict['bag_of_words'][3].append(recommendation)

        output_dict['top_words'][0].append(source)
        for i, word in enumerate(words_list[0:10]):
            output_dict['top_words'][i+1].append(word[0])

    return output_dict
