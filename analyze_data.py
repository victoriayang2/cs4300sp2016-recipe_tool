from __future__ import print_function
import numpy as np
import json
import glob
import nltk
#from nltk.stem.porter import *
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

print('cups' in units)

ing_raw = [r['ing'] for r in recipes]
ing_parsed = []

for i,ing_list in enumerate(ing_raw):
    ing_list_parsed = []
    for ing in ing_list:
        tokens = nltk.word_tokenize(ing.encode("ascii", "ignore"))
        pos_tags = nltk.pos_tag(tokens)
        nouns = [re.sub("[^a-zA-Z]", "", pair[0]) for pair in pos_tags if (pair[1] == 'NNS' or pair[1] == 'NN') and not pair[0].strip() in units]
        joined = " ".join(nouns)
        ing_list_parsed.append(joined)
    ing_parsed.append(ing_list_parsed)

ing_all = []
for line in ing_parsed:
    ing_all += line

counter = Counter(ing_all)
print(counter.most_common(100))