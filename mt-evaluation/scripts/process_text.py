# -*- coding: utf-8 -*-
#Input tokenized file.
#import string
import sys
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize

stemmer = PorterStemmer()

_PUNC_TOKENS = {
    '.',
    ',',
    '!',
    '?',
    ';',
    ':',
    '&',
    '%',
    '$',
    '*',
    '(',
    ')',
    '{',
    '}',
    '[',
    ']',
    '-',
    '--',   # Two hyphens
    '---',  # Three hyphens
    '—',    # EM DASH
    "'",
    '"',
    "''",
    '``',
    '"',  # LEFT DOUBLE QUOTATION MARK
    '"',  # RIGHT DOUBLE QUOTATION MARK
    }

def depunctuate(sent):
    return sent.rstrip().translate(str.maketrans('', '', '.,!?;:&%$*()}{][-\'\"'))

def porter_stem(sent):
    words = line.rstrip().split()
    return ' '.join([stemmer.stem(word.decode('utf-8')) for word in words])

if __name__ == "__main__":
    out_file = open(sys.argv[1]+"."+sys.argv[2],'w')
    with open(sys.argv[1],'r') as infile:
        for idx, line in enumerate(infile):
            #print idx, line
            #line = line.translate(str.maketrans('', '', '.,!?;:&%$*()}{][-\'\"'))
            #words = line.rstrip().split()
            #print words
            #try:
            #out_file.write((' '.join([stemmer.stem(word.decode('utf-8')) for word in words])+'\n').lower())
            #out_file.write((' '.join([word.lower() for word in words])+'\n'))
            #except UnicodeDecodeError:
            #    print idx, line
            if sys.argv[2] == 'depunct':
                out_file.write(depunctuate(line)+"\n")
            elif sys.argv[2] == 'stem':
                out_file.write(porter_stem(line)+"\n")
            elif sys.argv[2] == 'lower':
                out_file.write(line.lower()+"\n")
out_file.close()
