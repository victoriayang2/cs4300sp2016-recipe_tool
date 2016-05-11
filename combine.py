#!/usr/local/bin/python

import sqlite3
from scipy import sparse, io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import numpy as np
import glob
import json
import pickle
import random
from scipy.stats import t
from numpy import average, std
from math import sqrt

conn = sqlite3.connect('db.sqlite3')
print "Connected"

# with open("data/ratings.npy", "rb") as f:
#     ratings = np.load(f)

# with open("data/times.npy", "rb") as f:
#     times = np.load(f)

# with open("data/rec_svd_normalized.npy", "rb") as f:
#     rec_svd = np.load(f)

# with open("data/rev_rec_compressed.npy", "r") as f:
#     rev_by_rec = np.load(f)

# recipe_by_titles = io.mmread("data/recipe_by_titles.mtx").tocsr().toarray()

# recipe_by_verbs = io.mmread("data/recipe_by_verbs.mtx").tocsr().toarray()

# ingredient = rec_svd.dot(rec_svd.transpose())
# review = rev_by_rec.dot(rev_by_rec.transpose())
# title = recipe_by_titles.dot(recipe_by_titles.transpose())
# verb = recipe_by_verbs.dot(recipe_by_verbs.transpose())


# ratings_bytes = ratings.tostring()
# times_bytes = times.tostring()
# conn.execute("INSERT INTO metadata (ratings, times) VALUES (?, ?);", (sqlite3.Binary(ratings_bytes), sqlite3.Binary(times_bytes)))

# print "Inserted Metadata"

# combined = 0.5 * (0.35*ingredient + 0.65*review) + 0.05*title + 0.05*verb

# num_rec, _ = combined.shape
# for i in range(num_rec):
# 	bytes = combined[i].tostring()
# 	conn.execute("INSERT INTO combined (recipe, scores) VALUES (?, ?);", (i, sqlite3.Binary(bytes)))
# print "Inserted Combined"
# conn.commit()

cursor = conn.execute("SELECT SCORES FROM combined WHERE RECIPE = {}".format(0))
score = np.fromstring(cursor.fetchone()[0])
print score[0]
print score.shape
print "Select completed"

conn.close()
print "Connection closed"
