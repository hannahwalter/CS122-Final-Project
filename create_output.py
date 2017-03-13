import datetime as dt
import words_scraper
import stock_scraper
import naive_bayes
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

    output_dict = {}

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
        output_dict['bag_of_words'] = [['positive words'], ['negative words'], ['recommendation']]
        output_dict['top_words'] = []
        tweets = words_scraper.get_tweets(ticker, begin_date, end_date)
        daily_words_list, total_words_list = (words_scraper
            .get_twitter_words(tweets, ticker))
        
        t_top_words = total_words_list[0:10]
        for i, word in enumerate(t_top_words):
            output_dict['top_words'].append([str(i+1), word[0]])

        t_p_percentage, t_n_percentage = (words_scraper.
            bag_of_words_score(total_words_list))
        t_recommendation = util.recommendation(t_p_percentage, 
            t_n_percentage)
        output_dict['bag_of_words'][0].append(t_p_percentage)
        output_dict['bag_of_words'][1].append(t_n_percentage)
        output_dict['bag_of_words'][2].append(t_recommendation)
        
    if args['bag_of_words'] or args['naive_bayes']:
        nyt_urls = words_scraper.get_nyt_urls(company_name, begin_date, end_date)
        if type(nyt_urls) == str:
            output_dict['bag_of_words_error'] = nyt_urls
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
            nyt_words_list = words_scraper.split_strings_into_list(nyt_articles_list, company_name)
            n_p_percentage, n_n_percentage = words_scraper.bag_of_words_score(nyt_words_list)
            n_recommendation = util.recommendation(n_p_percentage, n_n_percentage)

            output_dict['bag_of_words'][0].append(n_p_percentage)
            output_dict['bag_of_words'][1].append(n_n_percentage)
            output_dict['bag_of_words'][2].append(n_recommendation)

            for i, word in enumerate(nyt_words_list[0:10]):
                output_dict['top_words'][i].append(word[0])

        if sa_continue:
            sa_words_list = words_scraper.split_strings_into_list(sa_articles_list, ticker)
            sa_p_percentage, sa_n_percentage = words_scraper.bag_of_words_score(sa_words_list)
            sa_recommendation = util.recommendation(sa_p_percentage, sa_n_percentage)

            output_dict['bag_of_words'][0].append(sa_p_percentage)
            output_dict['bag_of_words'][1].append(sa_n_percentage)
            output_dict['bag_of_words'][2].append(sa_recommendation)

            for i, word in enumerate(sa_words_list[0:10]):
                output_dict['top_words'][i].append(word[0])


        output_dict['Inaccessible Count'] = (sa_scrape_inaccessible + sa_articles_inaccessible 
            + nyt_inaccessible)

    if args['monte_carlo']:
        dates, monte_carlo, stock = words_scraper.monte_carlo(daily_words_list, ticker, 5000)
        output_dict['monte_carlo'] = [['dates'] + dates, ['monte carlo'] + monte_carlo, ['stock'] + stock]

    if args['naive_bayes'] and nyt_continue:
        output_dict['naive_bayes'] = [['positive articles'], ['negative articles'], ['recommendation']]

        pos_train, neg_train = naive_bayes.gen_train_list(40, 40)
        pos_model = naive_bayes.Bayes(pos_train, 1, "positive")
        neg_model = naive_bayes.Bayes(neg_train,1,"negative")

        result_tup = naive_bayes.mass_class(pos_model, neg_model, nyt_articles_list, 1)
        nb_p_percentage = result_tup[0]
        nb_n_percentage = result_tup[1]
        nb_recommendation = util.recommendation(nb_p_percentage, nb_n_percentage)

        output_dict['naive_bayes'][0].append(nb_p_percentage)
        output_dict['naive_bayes'][1].append(nb_n_percentage)
        output_dict['naive_bayes'][2].append(nb_recommendation)
 
    return output_dict
