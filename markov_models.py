import sys
import math
import re

class Markov:

    def __init__(self,k,s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"
        '''
        self.s = s
        self.k = k
        self.kchar = {}
        self.kcompchar = {}
        self.countk()

    def get_grams(self, s):
        '''
        extracts the k+1 grams from the string s and returns as a list
        '''
        comp_gram = []
        for i in range(self.k, len(s)):
            c_subs = s[i-self.k: i+1]
            comp_gram.append(c_subs)
        for i in range (self.k):
            c_subs = s[i - self.k:] + s[: i+1]
            comp_gram.append(c_subs)
        return comp_gram

    def countk(self):
        '''
        counts the frequency of the k grams and k+1 grams from the string
        stores the information in the values of the kcompchar (for k+1 grams)
        and kchar (for grams of k preceding characters) methods
        '''
        grams = self.get_grams(self.s)
        for gram in grams:
            subs = gram[:-1]
            if gram in self.kcompchar:
                self.kcompchar[gram]+=1
            if gram not in self.kcompchar:
                self.kcompchar[gram] = 1
            if subs in self.kchar:
                self.kchar[subs]+=1
            if subs not in self.kchar:
                self.kchar[subs]= 1    
        pass
    def log_probability(self,s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.
        '''
        
        prob_list = []
        probability = 0
        S = len(set(list(self.s)))
        
        grams = self.get_grams(s)

        for gram in grams:
            subs = gram[:-1]
            if gram in self.kcompchar:
                M = self.kcompchar[gram]
            else:
                M = 0
            num = M+1 
            if subs in self.kchar:
                N = self.kchar[subs]
            else:
                N = 0 
            prob = num /(N+S)
            
            log_prob = math.log(prob)
            prob_list.append(log_prob)

        probability = sum(prob_list)

        return probability




def identify_speaker(speech1, speech2, speech3, order):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the *normalized* log probabilities of each of the speakers
    uttering that text under a "order" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''
    model1 = Markov(order, speech1)
    model2 = Markov(order, speech2)

    log_prob1 = model1.log_probability(speech3)
    log_prob2 = model2.log_probability(speech3)

    norm_1 = log_prob1/ len(speech3)
    norm_2 = log_prob2/len(speech3)

    conclusion = None

    if norm_1 >= norm_2:
        conclusion = 'A'
    if norm_2 > norm_1:
        conclusion = 'B'
    return (norm_1, norm_2, conclusion)



def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''
    (likelihood1, likelihood2, conclusion) = res_tuple
    
    print("Speaker A: " + str(likelihood1))
    print("Speaker B: " + str(likelihood2))

    print("")

    print("Conclusion: Speaker " + conclusion + " is most likely")


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

    res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)
