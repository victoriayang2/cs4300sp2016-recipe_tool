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
tfidf_vec = TfidfVectorizer(binary=True, norm=None, use_idf=False, smooth_idf=False, tokenizer=custom_tokenizer,
                            stop_words='english',max_df=0.8, min_df=10, max_features=n_feats)

all_verbs = [",".join(rec['verbs']) for rec in recipes]
recipe_by_verbs = tfidf_vec.fit_transform(all_verbs)
verbs_by_recipe = sparse.csr_matrix.transpose(recipe_by_verbs)
all_titles = [",".join(rec['name']) for rec in recipes]
recipe_by_titles = tfidf_vec.fit_transform(all_titles)
titles_by_recipe = sparse.csr_matrix.transpose(recipe_by_titles)






