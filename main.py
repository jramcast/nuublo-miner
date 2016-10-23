#!/usr/bin/env python3

# First tests following this tutorial
# https://marcobonzanini.com/2015/03/09/mining-twitter-data-with-python-part-2/
# TODO: Refactor

from pymongo import MongoClient
from pprint import pprint
from nltk.tokenize import TweetTokenizer
from collections import Counter
from nltk.corpus import stopwords
from nltk import bigrams
from operator import itemgetter 
import string
import sys
from collections import defaultdict
import pandas
import vincent
 
com = defaultdict(lambda : defaultdict(int))
 
punctuation = list(string.punctuation)
stop = stopwords.words('english') + stopwords.words('spanish') + punctuation + ['rt', 'via', '…', '...']

tokenizer = TweetTokenizer()

def preprocess(text, lowercase=False):
    return tokenizer.tokenize(text.lower())

client = MongoClient('mongodb://localhost:27017/')
db = client.nuublo
count_terms = Counter()
count_all = Counter()
count_hash = Counter()
search_word = sys.argv[1] # pass a term as a command-line argument
count_search = Counter()
dates_search = []

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



## Get data from current conditions collection
conditions_counter = Counter()
conditions_cities = {}
for conditions in db.conditions.find():
    obs = conditions.get('current_observation')
    loc = conditions.get('location')
    if obs:
        conditions_counter.update([obs['weather']])
    if loc and obs:
        if 'Rain' in obs['weather']:
            city = loc.get('city', 'unknown')
            city_rain = conditions_cities.get(city, [])
            city_rain.append(obs['local_time_rfc822'])
            conditions_cities[city] = city_rain
        
print("************ Conditions ********")
pprint(conditions_counter.most_common(20))

# a list of "1" to count the hashtags
ones = [1]*len(dates_search)
# the index of the series
idx = pandas.DatetimeIndex(dates_search)
# the actual series (at series of 1s for the moment)
search_series = pandas.Series(ones, index=idx)
# Resampling / bucketing
per_hour = search_series.resample('1H').sum().fillna(0)

all_data_dict = {
    'tweets ' + search_word: per_hour
}

for k,v in conditions_cities.items():
    # a list of "1" to count the hashtags
    ones = [1]*len(v)
    # the index of the series
    idx = pandas.DatetimeIndex(v)
    # the actual series (at series of 1s for the moment)
    conditions_cities_series = pandas.Series(ones, index=idx)
    # Resampling / bucketing
    all_data_dict[k] = conditions_cities_series.resample('1H').sum().fillna(0)

# we need a DataFrame, to accommodate multiple series
dframe = pandas.DataFrame(data=all_data_dict, index=per_hour.index)

dframe = dframe.resample('1H').sum().fillna(0)

time_chart = vincent.Line(dframe[['tweets ' + search_word] + [k for k,v in conditions_cities.items()]])
time_chart.axis_titles(x='Time', y='Freq')
time_chart.legend(title='tweets vs conditions')
time_chart.to_json('time_chart.json')
