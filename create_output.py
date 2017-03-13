import datetime as dt

import words_scraper
import stock_scraper_v3
import naive_bayes
import util

def create_output(args):
    '''
    Master function to aggregate all our code into the appropriate 
    output format.

    INPUTS:
        args: dictionary with the following keys:
            company_name: name of company
            date: date to scrape up until
            days: number of days to scrape for before date
            bag_of_words, monte_carlo, naive_bayes: Boolean, if this analysis 
                is desired
    OUTPUTS:
        dictionary with the desired data
    '''

    

    name = args['company_name']
    date = args['date']
    days = args['days']

    # Generating appropriate isoformat dates
    end_date_obj = dt.datetime.strptime(date, '%Y-%m-%d').date()
    delta_obj = dt.timedelta(days)
    begin_date_obj = end_date_obj - delta_obj

    end_date = date
    begin_date = begin_date_obj.isoformat()

    # Finding company ticker
    find_ticker_company = stock_scraper_v3.find_ticker_company(name)

    if len(find_ticker_company) != 2:
        return find_ticker_company
    else:
        company_name = find_ticker_company['name']
        ticker = find_ticker_company['ticker']

    output_dict = {}
    nyt_continue = True
    sa_continue = True

    nyt_inaccessible = 0
    sa_articles_inaccessible = 0
    sa_scrape_inaccessible = 0

    if args['bag_of_words'] or args['monte_carlo']:
        output_dict['bag_of_words'] = {}
        tweets = words_scraper.get_tweets(ticker, begin_date, end_date)
        daily_words_list, total_words_list = (words_scraper
            .get_twitter_words(tweets, ticker))
        
        t_top_words = total_words_list[0:10]
        t_p_percentage, t_n_percentage = (words_scraper.
            bag_of_words_score(total_words_list))
        t_recommendation = util.recommendation(t_p_percentage, 
            t_n_percentage)
        t_percentage_string = ('Our bag of words analysis for Twitter found {}% '
            'positive words and {}% negative words.'.format(t_p_percentage, 
            t_n_percentage))
        
        output_dict['bag_of_words']['Twitter'] = {'Percentages': t_percentage_string, 
                                'Words': t_top_words, 'Recommendation': t_recommendation}

    if args['bag_of_words'] or args['naive_bayes']:
        nyt_urls = words_scraper.get_nyt_urls(company_name, begin_date, end_date)
        if type(nyt_urls) == str:
            output_dict['bag_of_words']['NYtimes'] = nyt_urls
            nyt_continue = False
        else:
            nyt_articles_list, nyt_inaccessible = (words_scraper.
                scrape_nyt_urls(nyt_urls, company_name))

        sa_urls = words_scraper.get_sa_urls(ticker, begin_date, end_date)
        if type(sa_urls) == str:
            output_dict['bag_of_words']['Seeking Alpha'] = sa_urls
            sa_continue = False
        else:
            sa_scrape_inaccessible = sa_urls[1]
            sa_articles_list, sa_articles_inaccessible = words_scraper.scrape_sa_urls(sa_urls[0])

    if args['bag_of_words']:
        if nyt_continue:
            nyt_words_list = words_scraper.split_strings_into_list(nyt_articles_list, company_name)
            n_p_percentage, n_n_percentage = words_scraper.bag_of_words_score(nyt_words_list)
            n_recommendation = util.recommendation(n_p_percentage, n_n_percentage)

            n_percentage_string = ('Our bag of words analysis for New York Times found {}% '
                'positive words and {}% negative words.'.format(n_p_percentage, n_n_percentage))
            
            output_dict['bag_of_words']['NYtimes'] = {'Percentages': n_percentage_string, 'Words': 
                nyt_words_list[0:10], 'Recommendation': n_recommendation}

        if sa_continue:
            sa_words_list = words_scraper.split_strings_into_list(sa_articles_list, ticker)
            sa_p_percentage, sa_n_percentage = words_scraper.bag_of_words_score(sa_words_list)
            sa_recommendation = util.recommendation(sa_p_percentage, sa_n_percentage)

            sa_percentage_string = ('Our bag of words analysis for Seeking Alpha found {}% '
                'positive words and {}% negative words.'.format(sa_p_percentage, sa_n_percentage))
            
            output_dict['bag_of_words']['Seeking Alpha'] = {'Percentages': sa_percentage_string, 'Words': 
                sa_words_list[0:10], 'Recommendation': sa_recommendation}

        output_dict['Inaccessible Count'] = (sa_scrape_inaccessible + sa_articles_inaccessible 
            + nyt_inaccessible)

    if args['monte_carlo']:
        words_scraper.monte_carlo(daily_words_list, ticker, 5000)

    if args['naive_bayes']:
        if nyt_continue:
            output_dict['naive_bayes'] = {}
            pos_train, neg_train = naive_bayes.gen_train_list(40, 40)
            pos_model = naive_bayes.Bayes(pos_train, 1, "positive")
            neg_model = naive_bayes.Bayes(neg_train,1,"negative")

            result_tup = naive_bayes.mass_class(pos_model, neg_model, nyt_articles_list, 1)
            nb_p_percentage = result_tup[0]
            nb_n_percentage = result_tup[1]
            nb_recommendation = util.recommendation(nb_p_percentage, nb_n_percentage)

            nb_percentage_string = ('Our Naive Bayes analysis for New York Times found '
                '{}% positive articles and {}% negative articles.'.format(nb_p_percentage, 
                nb_n_percentage))

            output_dict['naive_bayes']['Percentages'] = nb_percentage_string
            output_dict['naive_bayes']['Recommendation'] = nb_recommendation
        else:
            output_dict['naive_bayes'] = 'There were no articles for this company and timeframe'
    
    return output_dict
