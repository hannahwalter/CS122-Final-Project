import pandas
import numpy
import scipy
import naive_bayes
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer



def build_df(train_list, classification):
    rows = []
    index = []
    for fil in train_list:
        text = open(fil,"r").read()
        rows.append({'text': text, 'class': classification})
        index.append(fil)
    dataframe = pd.Dataframe(rows, index = index)
    return dataframe

def build_train(num_pos, num_neg):
    pos_train, neg_train = naive_bayes.gen_train_list(num_pos, num_neg)
    train_df = pd.Dataframe({'text': [], 'class':[]})
    pos_data = build_df(pos_train, 1)
    neg_data = build_df(neg_train, 0)
    train_df.append(pos_data)
    train_df.append(neg_data)
    train_df = train_df.reindex(numpy.random.permutation(train_df.index))

    return train_df

def classify_mnb(train_df, test_list):
    pipeline = Pipeline([
    ('count_vectorizer',   CountVectorizer(ngram_range=(1,  2))),
    ('tfidf_transformer',  TfidfTransformer()),
    ('classifier',         MultinomialNB())])
    pipeline.fit(train_df['text'].values, train_df['class'].values)
    predicts = pipeline.predict(test_list)
    return predicts





