from __future__ import print_function
import numpy as np
import json
import glob
import nltk
from nltk.stem.porter import *
from nltk.stem.wordnet import *
import random
import re
from collections import Counter

units_f = open('units')
units = [str(l).replace("\n", "") for l in units_f]
units_f.close()
recipes = []
path = 'jsons\chunk*.json'   
files=glob.glob(path)   
for file in files: 
    with open(file) as f:
        for line in f:
            recipes.append(json.loads(line))

wnl = WordNetLemmatizer()

ing_raw = [r['ing'] for r in recipes]
ing_parsed = []

remove_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'CC', 'DT', 'IN', 'RP', 'TO']
take_tags = ['NNS', 'NN', 'NNP', 'NNPS']
anomalies = []

print("PARSING")
for i,ing_list in enumerate(ing_raw):
    ing_list_parsed = []
    for j,ing in enumerate(ing_list):
        if not ":" in ing:
            ing = re.sub("\s+([-])\s+\w+|\d-", "", ing.encode("ascii", "ignore").lower())
            ing = re.sub("([^a-zA-Z'\-])|\s+(['])|(['])\s+", " ", ing)
            ing = re.sub("\s+([-])|([-])\s+", "", ing)
            tokens = [wnl.lemmatize(word) for word in nltk.word_tokenize(ing) if not word in units]
            pos_tags = nltk.pos_tag(tokens)
            if len(pos_tags) == 1:
                ing_list_parsed.append(pos_tags[0][0])
            else:
                remove_verbs = pos_tags
                diff = 1
                while diff > 0:
                    before = len(remove_verbs)
                    remove_verbs = [pair[0] for pair in remove_verbs if (not pair[1] in remove_tags)]
                    diff = before - len(remove_verbs)
                    remove_verbs = nltk.pos_tag(remove_verbs)
                #re_tag = nltk.pos_tag(remove_verbs)
                keep_tags = [pair[0] for pair in remove_verbs]
                if len(keep_tags) == 0:
                    anomalies.append((i,j))
                    print(remove_verbs)
                joined = " ".join(keep_tags)
                ing_list_parsed.append(joined)
    ing_parsed.append(ing_list_parsed)

ing_all = []
for line in ing_parsed:
    ing_all += line

print("ANOMALIES")
for pair in anomalies:
    print(ing_raw[pair[0]][pair[1]])

print("COMMONERS")
counter = Counter(ing_all)
print(counter.most_common(25))