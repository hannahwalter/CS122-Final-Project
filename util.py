'''
TEAM: FiSci
PEOPLE: Hannah Ni, Hannah Walter, Lin Su

This file provides commonly used functions.
'''

import re

def open_lexicon_files(file):
    f = open(file, 'r')

    words = []

    for line in f:
        if (line.startswith('{') or line.startswith('\\') or 
            line.startswith('}') or line.startswith(';') or line is '\n'):
            continue
        line = re.sub('\\\\\\n', '', line)
        words.append(line)

    return set(words)

def get_word_lexicons(positive = 'files_for_code/positive-words.txt', negative = 'files_for_code/negative-words.txt'):
    positive_set = open_lexicon_files(positive)
    negative_set = open_lexicon_files(negative)

    return positive_set, negative_set

def get_stop_words(words_file = 'files_for_code/stop_words.txt'):
    f = open(words_file, 'r')
    stop_words = set(f.read().splitlines())

    stop_words |= {'say', 'says', 'said', 'mr', 'like', 'likely', 'just', 
    'including', 'way', 'going', 'dont', 'cant', 'company', 'companies', 
    'percent'}

    return stop_words

def recommendation(p_percentage, n_percentage):

    if abs(p_percentage - n_percentage) < 10:
        return 'Hold'
    else:
        if p_percentage > n_percentage:
            return 'Buy'
        else:
            return 'Sell'

