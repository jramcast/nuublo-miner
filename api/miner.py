#!/usr/bin/env python3

# First methods inspired by tutorial
# https://marcobonzanini.com/2015/03/09/mining-twitter-data-with-python-part-2/
# TODO: Refactor

from pymongo import MongoClient
from nltk.tokenize import TweetTokenizer
from collections import Counter
from nltk.corpus import stopwords
from operator import itemgetter 
import string
from collections import defaultdict

punctuation = list(string.punctuation)
stopwords_list = stopwords.words('english') + stopwords.words('spanish') + punctuation + ['rt', 'via', '…', '...']

def select_most_frequent(number, include):
    """
    Prints the first "number" most frequent number of words
    """
    counter = Counter()
    db = _connect_to_db()
    create_terms_list = choose_terms_filter(include)
    for tweet in db.meteoTweets.find():
        terms = create_terms_list(tweet)
        counter.update(terms)
    return counter.most_common(number)


def select_most_frequent_coocurrences(number, include):
    """
    Gets coocurrences for a given word
    """
    com = defaultdict(lambda : defaultdict(int))
    db = _connect_to_db()
    create_terms_list = choose_terms_filter(include)
    for tweet in db.meteoTweets.find():
        # Count terms only (no hashtags, no mentions)
        terms = create_terms_list(tweet)
        # Build co-occurrence matrix
        for i in range(len(terms)-1):            
            for j in range(i+1, len(terms)):
                w1, w2 = sorted([terms[i], terms[j]])                
                if w1 != w2:
                    com[w1][w2] += 1
    # For each term, print the most common co-occurrent terms
    com_max = []
    for t1 in com:
        t1_max_terms = sorted(com[t1].items(), key=itemgetter(1), reverse=True)[:10]
        for t2, t2_count in t1_max_terms:
            com_max.append(((t1, t2), t2_count))
    # Get the most frequent co-occurrences
    terms_max = sorted(com_max, key=itemgetter(1), reverse=True)
    return terms_max[:number]


def select_most_frequent_word_coocurrences(word, number, include):
    """
    Select the most frequent coocurrences of a given word
    """
    counter = Counter()
    db = _connect_to_db()
    create_terms_list = choose_terms_filter(include)
    for tweet in db.meteoTweets.find():
        terms = create_terms_list(tweet)
        if word.lower() in terms:
            counter.update(terms)
    return counter.most_common(number)  


def _connect_to_db():
    client = MongoClient('mongodb://localhost:27017/')
    return  client.nuublo


def choose_terms_filter(include):
    default = lambda tweet: [term for term in _preprocess(tweet['text']) 
                            if term not in stopwords_list]
    if include == 'all':
        return default
    elif include == 'terms':
        return lambda tweet: [term for term in _preprocess(tweet['text']) 
            if term not in stopwords_list and
            not term.startswith(('#', '@'))] 
    elif inlude == 'hasthags': 
        return lambda tweet: [term for term in _preprocess(tweet['text']) if term.startswith('#')]
    else:
        return default


def _preprocess(text, lowercase=False):
    tokenizer = TweetTokenizer()
    return tokenizer.tokenize(text.lower())



"""
for tweet in db.meteoTweets.find():
    # Create a list with all the terms
    terms_all = [term for term in preprocess(tweet['text']) if term not in stop]
    terms_hash = [term for term in preprocess(tweet['text']) if term.startswith('#')]
    # Count terms only (no hashtags, no mentions)
    terms_only = [term for term in preprocess(tweet['text']) 
            if term not in stop and
            not term.startswith(('#', '@'))] 
            # mind the ((double brackets))
            # startswith() takes a tuple (not a list) if 
            # we pass a list of inputs

    # Build co-occurrence matrix
    for i in range(len(terms_only)-1):            
        for j in range(i+1, len(terms_only)):
            w1, w2 = sorted([terms_only[i], terms_only[j]])                
            if w1 != w2:
                com[w1][w2] += 1
    # Update the counters
    count_terms.update(terms_only)
    count_all.update(terms_all)
    count_hash.update(terms_hash)
    if search_word and search_word.lower() in terms_only:
        count_search.update(terms_only)
        dates_search.append(tweet['created_at'])

# Print the first 5 most frequent words
pprint(count_all.most_common(20))
pprint(count_terms.most_common(20))
pprint(count_hash.most_common(20))
if search_word:
    pprint("************ Co-occurrence for %s ************" % search_word)
    pprint(count_search.most_common(20))

# For each term, print the most common co-occurrent terms
com_max = []
for t1 in com:
    t1_max_terms = sorted(com[t1].items(), key=itemgetter(1), reverse=True)[:10]
    for t2, t2_count in t1_max_terms:
        com_max.append(((t1, t2), t2_count))
# Get the most frequent co-occurrences
terms_max = sorted(com_max, key=itemgetter(1), reverse=True)
print("************ Most common co-ocurrent terms ********")
pprint(terms_max[:10])
"""
