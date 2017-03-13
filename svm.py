import pandas
import numpy
import scipy
import naive_bayes
from pandas import DataFrame
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cross_validation import KFold
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.linear_model import SGDClassifier, LogisticRegression


#learned to use package and took some structure of code 
#from sklearn examples 

def build_df(train_list, classification):
    rows = []
    index = []
    for fil in train_list:
        text = open(fil,"r").read()
        rows.append({'text': text, 'class': classification})
        index.append(fil)
    dataframe = pandas.DataFrame(rows, index = index)
    return dataframe

def build_train(num_pos, num_neg):
    pos_train, neg_train = naive_bayes.gen_train_list(num_pos, num_neg)
    train_df = pandas.DataFrame({'text': [], 'class':[]})
    pos_data = build_df(pos_train, 1)
    neg_data = build_df(neg_train, 0)
    train_df = train_df.append(pos_data)
    train_df = train_df.append(neg_data)
    train_df = train_df.reindex(numpy.random.permutation(train_df.index))

    return train_df

mnb_pipeline = Pipeline([
    ('count_vectorizer',   CountVectorizer(ngram_range=(1,  2))),
    ('tfidf_transformer',  TfidfTransformer()),
    ('classifier',         MultinomialNB())])

svm_pipeline = Pipeline([
    ('count_vectorizer',   CountVectorizer(ngram_range=(1,  2))),
    ('tfidf_transformer',  TfidfTransformer()),
    ('classifier',         SGDClassifier(loss='hinge', penalty='l2',
                                            alpha=1e-3, n_iter=5, random_state=42))])

maxent_pipeline = Pipeline([
    ('count_vectorizer',   CountVectorizer(ngram_range=(1,  2))),
    ('tfidf_transformer',  TfidfTransformer()),
    ('classifier',         LogisticRegression(random_state=42))])

def classify_with(train_df, test_list, pipeline):
    pipeline.fit(train_df['text'].values, train_df['class'].values)
    predicts = pipeline.predict(test_list)
    
    return predicts 

def final_output(num_pos, num_neg, test_list):
    df = build_train(num_pos, num_neg)
    results = []
    for classifier in [mnb_pipeline, maxent_pipeline, svm_pipeline]:
        predicts = classify_with(df, test_list, classifier)
        predicts = list(predicts)
        pos_art = sum(predicts)
        neg_art = len(predicts) - pos_art
        perc_pos = pos_art*100/len(predicts)
        perc_neg = neg_art*100/len(predicts)
        accuracy = test_clf(df, classifier)*100
        if classifier == mnb_pipeline:
            name = "Multinomial Naive Bayes Classifier Model"
        if classifier == maxent_pipeline:
            name = "Maximum Entropy Classifier Model"
        if classifier == svm_pipeline:
            name = "Support Vector Machine Classifier Model"
        return_list = [name, perc_pos, perc_neg, accuracy]
        results.append(return_list)
    return results

def test_clf(data, pipeline):
    k_fold = KFold(n=len(data), n_folds=6)
    scores = []

    for train_indices, test_indices in k_fold:
        train_text = data.iloc[train_indices]['text'].values
        train_y = data.iloc[train_indices]['class'].values

        test_text = data.iloc[test_indices]['text'].values
        test_y = data.iloc[test_indices]['class'].values

        pipeline.fit(train_text, train_y)
        predictions = pipeline.predict(test_text)

        score = f1_score(test_y, predictions, pos_label=1)
        scores.append(score)
    
    return sum(scores)/len(scores)