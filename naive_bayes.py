import sys
import math
import re

#took some structure of code from markov modes PA

PRIOR_PROB_POS = .5
PRIOR_PROB_NEG = .5

class Bayes:
    def __init__(self, train_list, k, sign):
        self.train_list = train_list
        self.k = k
        self.sign = sign
        self.grams = {}
        self.num_words = 0
        self.train_all()

    def get_k_words(self, word_list):
        '''
        generates k word grams from the word_list
        returns the list of k word grams
        '''
        ret_list = []
        for i in range(len(word_list)-self.k+1):
            gram = word_list[i:i+self.k+1]
            string_gram= " ".join(gram)
            ret_list.append(string_gram)
        return ret_list

    def train(self, word_list):
        '''
        adds the k grams of a given word list to the model 
        '''
        self.num_words+= len(word_list)
        gram_list = self.get_k_words(word_list)
        for gram in gram_list:
            if gram not in self.grams:
                self.grams[gram] = 1
            if gram in self.grams:
                self.grams[gram]+=1
        
    def train_all(self):
        '''
        trains the model on all of the files in the train_list 
        ''' 
        for fil in self.train_list:
            txt = open(fil, "rU").read()
            txt_list = re.sub("[^\w]", " ",  txt).split()
            self.train(txt_list)
        pass

    def get_probs(self, test_stg):
        '''
        get's the un-normalized probability that a test_stg is in 
        the class of the model
        '''
        test_list = re.sub("[^\w]", " ",  test_stg).split()
        test_grams = self.get_k_words(test_list)
        prob_list = []
        V = self.num_words
        for gram in test_grams:
            count = 0
            if gram not in self.grams:
                count = 1
            if gram in self.grams:
                count = self.grams[gram]+1
            prob = count/V
            log_prob = math.log(prob)
            prob_list.append(log_prob)
        sum_probs = sum(prob_list)
        if self.sign == "positive":
            ret_prob = math.log(PRIOR_PROB_POS) + sum_probs
        else:
            ret_prob = math.log(PRIOR_PROB_NEG) + sum_probs
        return ret_prob

def gen_train_list(num_pos, num_neg):
    '''
    generates the list of training files given the number
    of positive and negative files 
    relies on our naming convention for training files
    '''
    pos_train = []
    neg_train = []
    for i in range(num_pos):
        pos_file = "positive_train/pos_"+str(i+1)+".txt"
        pos_train.append(pos_file)
    for i in range(num_neg):
        neg_file = "negative_train/neg_"+ str(i+1)+".txt"
        neg_train.append(neg_file)
    return pos_train, neg_train

def mass_class(pos_model, neg_model, test_list, order):
    '''
    given a positive and negative model classifies each
    text in a list of texts as positive or negative
    returns a tuple of the percentage positive, percentage negative
    '''
    pos_count = 0
    neg_count = 0

    for test_text in test_list:
        len_test = len(re.sub("[^\w]", " ",  test_text).split())
        pos_prob = pos_model.get_probs(test_text)/len_test
        neg_prob = neg_model.get_probs(test_text)/len_test
        if pos_prob >= neg_prob:
            pos_count +=1
        if pos_prob < neg_prob:
            neg_count+=1
    pos_perc = pos_count*100/(pos_count+neg_count)
    neg_perc = neg_count*100/(pos_count+neg_count)
    return (pos_perc,neg_perc)

def classify(pos_list, neg_list, test_text, order):
    '''
    classifies an individual text given a list of positive and negative
    training files.  
    outputs a tuple of the probability the text is negative, 
    the probability the text is positive, and a conclusion
    '''
    len_test = len(re.sub("[^\w]", " ",  test_text).split())

    pos_model = Bayes(pos_list, order, "positive")
    pos_prob = pos_model.get_probs(test_text)/len_test

    neg_model = Bayes(neg_list, order, "negative")
    neg_prob = neg_model.get_probs(test_text)/len_test

    conclusion = None
    if pos_prob >= neg_prob:
        conclusion = "Positive"
    if pos_prob < neg_prob:
        conclusion = "Negative"

    return (pos_prob, neg_prob, conclusion)

def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''
    (likelihood1, likelihood2, conclusion) = res_tuple
    
    print("Positive: " + str(likelihood1))
    print("Negative: " + str(likelihood2))

    print("")

    print("Conclusion: This article is most likely " + conclusion)


if __name__=="__main__":
    num_args = len(sys.argv)

    if num_args != 5:
        print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
              "<file name for speaker B>\n  <file name of text to identify> " +
              "<order>")
        sys.exit(0)
    
    with open(sys.argv[1], "rU") as file1:
        speech1 = file1.read()

    with open(sys.argv[2], "rU") as file2:
        speech2 = file2.read()

    with open(sys.argv[3], "rU") as file3:
        speech3 = file3.read()

    res_tuple = classify(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)










