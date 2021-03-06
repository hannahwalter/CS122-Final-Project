# CS122-Final-Project SciFi

Who we are:
Hannah Ni, Hannah Walter, Lin Su

What we have done:
1. Through trial and error, we attempted to draw from three types of stock commentary sources: social apps, new articles, and stock blogs. We managed to scrape Twitter, New York Times, and Seeking Alpha to represent these outlets.
2. After scraping the appropriate tweets and articles, we used a bag-of-words method and additional
sentiment classifier model to gauge sentiment.
3. We also used a random Monte-Carlo simulation assess how well sentiment follows real stock movement.
4. We presented our results in an intuitive web interface with tables and graphs customizable to how much detail the user desires to see.

How to try our work:
1. Install APIs (for yahoo_finance, see Appendix of this text)
2. Navigate to the folder this text file is in, run command $ python3 manage.py runserver
3. Open a browser and go to 'http://127.0.0.1:8000/'
4. Get a feel of our intuitive user interface and try it out
5. Having trouble finding the ticker or name of a company? Don't worry, we will let you know if your input is contained in any tickers. We have also designed a program to help you out. In the command line, run the file 'interactive_stock_ticker_search_command_line', and follow the intuitive instructions on the command line to easily find the ticker of the company you are interested in.

What challenges we have tried to conquer:
1. Scraping our sources: While NYTimes provided an API for us to use, Twitter's API did not provide the desired flexibility, and Seeking Alpha had no API at all. As a result, we had to find a way to scrape these sources the traditional way. In order to prevent being blocked for scraping, our code implements some pauses which can slow the data gathering process. Furthermore, the use of "infinite scrolling" proved more difficult to deal with. Even now, some of our web scrapers will not retrieve
results, so there are many, many corner cases we had to deal with (invalid requests, no articles, etc.)
2. Data analysis: Because of the sentiment deeply embedded in the contextual nuances of an article, our intial Naive Bayes sentiment classifier was not as successful as we hoped. More sophisticated methods like the sklearn module were better at classifying as a positive article may list several negative things a company has gone through before presenting future outlooks.
3. Time: Due to scraping on the spot, our code takes a while to run and process. While this is not ideal, it is an unfortunate consequence of our scraping. 

What our potential could be if we had more time:
1. Train an algorithm that weights each data source and method. If we had more time, we would run our analysis on thousands of stocks with data for the past decade, draw recommendation from each of the analysis, and simulate the payoff we would get by following each recommendation sources. From this we would derive better recommendation based on high-dimensional datasets. For example, we are suspecting that the most accurate source of prediction may differ by the industry, and that in the past decade, Twitter may be a more and more accurate predictor. This historical backtesting is not feasible now
given the time it takes to run our code and space constraints.
2. Improve the scope of sources we are scraping. We look forward to scraping Wall Street Journal, the Economist, and other high-profile commentary sources. Currently these sites restricts us from beautifulsoup or selenium scraping. With more authoritative sources, we could make better recommendation.
3. Improving the sentiment library. Currently we collected 100 articles and classified them into positive and negative articles. Our Naive Bayes prediction would be significantly more accurate as we increase the number and quality of our training materials.

Appendix:
Yahoo_finance installation guide:
1. Open https://pypi.python.org/pypi/yahoo-finance in your browser
2. Search for yahoo-finance-1.4.0.tar.gz on this page
3. Download the installation package
4. Navigate to the download folder in command line
5. Run the command: $ sudo python setup.py install
6. Replace the file yql.py in the folder yahoo-finance-1.4.0 with the attached updated file (there are some bugs in the downloaded package and we fixed them)
