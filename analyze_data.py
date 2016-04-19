from __future__ import print_function
import numpy as np
import json
import glob
import nltk
from nltk.stem.porter import *
import random
import re
from collections import Counter

units_f = open('units')
units = [str(l).replace("\n", "") for l in units_f]
units_f.close()
recipes = []
path = 'jsons\chunk1.json'   
#files=glob.glob(path)   
#for file in files: 
#    with open(file) as f:
#        for line in f:
#            recipes.append(json.loads(line))
with open(path) as f:
    for line in f:
        recipes.append(json.loads(line))

stemmer = PorterStemmer()

ing_raw = [r['ing'] for r in recipes]
ing_parsed = []

take_tags = ['NNS', 'NN', 'NNP', 'NNPS', 'IN', 'JJ']
anomalies = []

for i,ing_list in enumerate(ing_raw):
    ing_list_parsed = []
    for j,ing in enumerate(ing_list):
        if not ":" in ing:
            ing = re.sub("[^a-zA-Z]", " ", ing.encode("ascii", "ignore").lower())
            tokens = [word for word in nltk.word_tokenize(ing) if not word in units]
            pos_tags = nltk.pos_tag(tokens)
            if len(pos_tags) == 1:
                if pos_tags[0][1] in take_tags:
                    ing_list_parsed.append(stemmer.stem(pos_tags[0][0]))
                else:
                    ing_list_parsed.append(pos_tags[0][0])
            else:
                nouns = [stemmer.stem(pair[0]) for pair in pos_tags if (pair[1] in take_tags)]
                if len(nouns) == 0:
                    anomalies.append((i,j))
                    print(pos_tags)
                joined = " ".join(nouns)
                ing_list_parsed.append(joined)
    ing_parsed.append(ing_list_parsed)

ing_all = []
for line in ing_parsed:
    ing_all += line

for pair in anomalies:
    print(ing_raw[pair[0]][pair[1]])

#counter = Counter(ing_all)
#print(counter.most_common(100))