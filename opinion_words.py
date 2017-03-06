import re

def open_file(file):
    f = open(file, 'r')

    words = []

    for line in f:
        if (line.startswith('{') or line.startswith('\\') or 
            line.startswith('}') or line.startswith(';') or line is '\n'):
            continue
        line = re.sub('\\\\\\n', '', line)
        words.append(line)

    return set(words)

def get_word_lexicons(positive = 'positive-words.txt', negative = 'negative-words.txt'):
    positive_set = open_file(positive)
    negative_set = open_file(negative)

    return positive_set, negative_set

