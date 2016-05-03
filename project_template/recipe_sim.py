from __future__ import print_function
import numpy as np
import json
import glob 
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
from scipy import sparse, io
from sklearn.feature_extraction.text import TfidfVectorizer


recipes = []
path = 'jsons/parsed*.json'   
files=glob.glob(path)   
for file in files: 
    with open(file) as f:
        for line in f:
            recipes.append(json.loads(line))


def custom_tokenizer(terms):
    return terms.split(",")

n_feats = 5000
tfidf_vec1 = TfidfVectorizer(norm='l2', use_idf=False, smooth_idf=False, tokenizer=custom_tokenizer,
                            max_features=n_feats)
tfidf_vec2 = TfidfVectorizer(norm='l2', use_idf=False, smooth_idf=False, tokenizer=custom_tokenizer,
                            stop_words='english',max_features=n_feats)

all_verbs = [",".join(rec['verbs']) for rec in recipes]
recipe_by_verbs = tfidf_vec1.fit_transform(all_verbs)
verbs_by_recipe = sparse.csr_matrix.transpose(recipe_by_verbs)
all_titles = [",".join(tokenizer.tokenize(rec['name'])) for rec in recipes]
recipe_by_titles = tfidf_vec2.fit_transform(all_titles)
titles_by_recipe = sparse.csr_matrix.transpose(recipe_by_titles)
title_words_by_index = {word:i for i,word in enumerate(tfidf_vec2.get_feature_names())}
verb_words_by_index = {verb:i for i,verb in enumerate(tfidf_vec1.get_feature_names())}

with open("./data/recipe_by_verbs.npy", "r") as f1:
	np.save(f1, recipe_by_verbs)

with open("./data/recipe_by_titles.npy", "r") as f2:
	np.save(f2, recipe_by_titles)

with open("./data/title_words_by_index.json", "r") as f3:
	np.save(f3, title_words_by_index)

with open("./data/verb_words_by_index.json", "r") as f4:
	np.save(f4, verb_words_by_index)






