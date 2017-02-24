import re

def open_file(file = 'positive-words.txt'):
    f = open(file, 'r')

    words = []

    for line in f:
        if (line.startswith('{') or line.startswith('\\') or 
            line.startswith(';') or line is '\n'):
            continue
        line = re.sub('\\\\\\n', '', line)
        words.append(line)

    return words
