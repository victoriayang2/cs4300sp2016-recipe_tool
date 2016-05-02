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
tfidf_vec1 = TfidfVectorizer(norm=None, use_idf=False, smooth_idf=False, tokenizer=custom_tokenizer,
                            max_features=n_feats)
tfidf_vec2 = TfidfVectorizer(norm=None, use_idf=False, smooth_idf=False, tokenizer=custom_tokenizer,
                            stop_words='english',max_features=n_feats)

all_verbs = [",".join(rec['verbs']) for rec in recipes]
recipe_by_verbs = tfidf_vec1.fit_transform(all_verbs)
verbs_by_recipe = sparse.csr_matrix.transpose(recipe_by_verbs)
all_titles = [",".join(tokenizer.tokenize(rec['name'])) for rec in recipes]
recipe_by_titles = tfidf_vec2.fit_transform(all_titles)
titles_by_recipe = sparse.csr_matrix.transpose(recipe_by_titles)
recipe_title_words_by_index = {word:i for i,word in enumerate(tfidf_vec2.get_feature_names())}






