'''
TEAM: FiSci
PEOPLE: Hannah Ni, Hannah Walter, Lin Su

This file provides advanced sentiment measures. We learned to use the sklearn package
and took some structure of code from sklearn API and examples.
'''

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


def build_df(train_list, classification):
    '''
    This function builds a pandas DataFrame from a training list

    INPUTS:
        train_list: list of file names of the training data
        classification: the classification associated with files
            in train list, 1 for positive, or 0 for negative
    OUTPUTS:
        dataframe: a pandas DataFrame of the info with the file name as index
            a column with the text, and a column with classification
    '''
    rows = []
    index = []
    for fil in train_list:
        text = open(fil,"r").read()
        rows.append({'text': text, 'class': classification})
        index.append(fil)
    dataframe = pandas.DataFrame(rows, index = index)
    return dataframe

def build_train(num_pos, num_neg):
    '''
    Builds the complete training dataframe given a number of positive
    or negative training articles

    INPUTS: number of positive and negative training articles
    OUTPUTS: the training DataFrame
    '''
    # generates the list of training files given num_pos and num_neg
    pos_train, neg_train = naive_bayes.gen_train_list(num_pos, num_neg)
    #intializes an empty DataFrame
    train_df = pandas.DataFrame({'text': [], 'class':[]})
    pos_data = build_df(pos_train, 1)
    neg_data = build_df(neg_train, 0)
    train_df = train_df.append(pos_data)
    train_df = train_df.append(neg_data)
    #reindexes using a random permutation to help with in sample testing
    train_df = train_df.reindex(numpy.random.permutation(train_df.index))

    return train_df

#initializes the Multinomial Naive Bayes Classifier
mnb_pipeline = Pipeline([
    ('count_vectorizer',   CountVectorizer(ngram_range=(1,  2))),
    ('tfidf_transformer',  TfidfTransformer()),
    ('classifier',         MultinomialNB())])

#initializes the support vector machine classifier
svm_pipeline = Pipeline([
    ('count_vectorizer',   CountVectorizer(ngram_range=(1,  2))),
    ('tfidf_transformer',  TfidfTransformer()),
    ('classifier',         SGDClassifier(loss='hinge', penalty='l2',
                                            alpha=1e-3, n_iter=5, random_state=42))])

#intializes the maximum entropy logistic regression classifier
maxent_pipeline = Pipeline([
    ('count_vectorizer',   CountVectorizer(ngram_range=(1,  2))),
    ('tfidf_transformer',  TfidfTransformer()),
    ('classifier',         LogisticRegression(random_state=42))])

def classify_with(train_df, test_list, pipeline):
    '''
    This function classifies a test_list of strings based on a 
    given training DataFrame and a given classifier
    INPUTS:
        train_df: the training DataFrame
        test_list: the list of strings to classify
        pipeline: the classifier to use
    OUTPUTS:
        predicts: an array of classifications, the index of the array corresponds
            to the index of the test_list 
    '''
    pipeline.fit(train_df['text'].values, train_df['class'].values)
    predicts = pipeline.predict(test_list)
    
    return predicts 

def final_output(num_pos, num_neg, test_list):
    '''
    Generates the final output to be passed through to our django file
    INPUTS:
        num_pos: number of positive training files
        num_neg: number of negative training files
        test_list: list of strings to be classified
    OUTPUTS:
        results: a list of lists for each classifier 
            each individual list is in the form:
            ['name of classifier', percent positive, 
                percent negative, accuracy]
    '''
    # builds training df
    df = build_train(num_pos, num_neg)
    results = []

    for classifier in [mnb_pipeline, maxent_pipeline, svm_pipeline]:
        predicts = classify_with(df, test_list, classifier)
        # turns predictions into list from an array
        predicts = list(predicts)
        # since positive is a 1, number of pos articles is sum of the predicts
        pos_art = sum(predicts)
        #all articles either pos or neg, so number neg 
        #is number of articles - number of pos
        neg_art = len(predicts) - pos_art
        perc_pos = pos_art*100/len(predicts)
        perc_neg = neg_art*100/len(predicts)
        #generate value for expected accuracy 
        accuracy = round(test_clf(df, classifier)*100, 2)
        if classifier == mnb_pipeline:
            name = "Multinomial Naive Bayes Classifier Model"
        if classifier == maxent_pipeline:
            name = "Maximum Entropy Classifier Model"
        if classifier == svm_pipeline:
            name = "Support Vector Machine Classifier Model"
        return_list = [name, round(perc_pos, 2), round(perc_neg, 2), accuracy]
        results.append(return_list)
    return results

def test_clf(train_df, pipeline):
    ''' 
    This function does in sample testing to assess accuracy of the Model
    INPUTS: 
        train_df: training DataFrame
        pipeline: the classifier to test
    OUTPUTS:
        score: a measure of accuracy
    '''
    #divides the training data into 6 samples
    #one testing and then 5 training
    k_fold = KFold(n=len(train_df), n_folds=6)
    scores = []

    #iterates through various combos of training and testing
    for train_indices, test_indices in k_fold:
        train_text = train_df.iloc[train_indices]['text'].values
        train_y = train_df.iloc[train_indices]['class'].values

        test_text = train_df.iloc[test_indices]['text'].values
        test_y = train_df.iloc[test_indices]['class'].values

        pipeline.fit(train_text, train_y)
        predictions = pipeline.predict(test_text)

        #computes the F1 score
        score = f1_score(test_y, predictions, pos_label=1)
        scores.append(score)
    
    return sum(scores)/len(scores)