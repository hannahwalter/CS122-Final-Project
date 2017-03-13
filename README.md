# CS122-Final-Project

Contributors: Hannah Ni, Hannah Walter, Lin Su

Through this project, we attempted to draw from three common sources of stock commentary: Twitter, new articles, and stock blogs. We scraped Twitter, New York Times, and Seeking Alpha to represent these outlets. After scraping the appropriate tweets and articles, we used a bag-of-words method and a naive-bayes model to gauge sentiment. We also used a random Monte-Carlo simulation assess how well sentiment follows stock movement.

To use our program:

Through this project, we ran into several challenges.

- Scraping our sources: While NYTimes provided an API for us to use, Twitter's API did not provide the desired flexibility, and Seeking Alpha had no API at all. As a result, we had to find a way to scrape these sources the traditional way. In order to prevent being blocked for scraping, our code implements some pauses which can slow the data gathering process. Furthermore, the use of "infinite scrolling" proved more difficult to deal with.

- Data analysis: Because of the sentiment deeply embedded in the contextual nuances of an article, our Naive Bayes predictor is not as successufl as one would hope. More sophisticated methods are likely necessary as a positive article may list several negative things a company has gone through before presenting future outlooks.

- Time: Due to scraping on the spot, our code takes a while to run and process. While this is not ideal, it is an unfortunate consequence of our scraping. 