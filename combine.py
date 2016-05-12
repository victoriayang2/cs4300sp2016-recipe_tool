#!/usr/local/bin/python

import psycopg2
import os
import sys
from scipy import sparse, io
import numpy as np
import json
import pickle

# conn = sqlite3.connect('db.sqlite3')
conn = psycopg2.connect(
    database='d7suj672n3qip',
    user='fpaekdihbgosnx',
    password=os.environ['DBPASS'],
    host='ec2-50-17-197-76.compute-1.amazonaws.com',
    port='5432'
)
print "Connected"
cursor = conn.cursor()

with open("data/unused/ratings.npy", "rb") as f:
    ratings = np.load(f)

with open("data/unused/times.npy", "rb") as f:
    times = np.load(f)

with open("data/unused/rec_svd_normalized.npy", "rb") as f:
    rec_svd = np.load(f)

with open("data/unused/rev_rec_compressed.npy", "r") as f:
    rev_by_rec = np.load(f)

recipe_by_titles = io.mmread("data/unused/recipe_by_titles.mtx").tocsr().toarray()

recipe_by_verbs = io.mmread("data/unused/recipe_by_verbs.mtx").tocsr().toarray()

ingredient = rec_svd.dot(rec_svd.transpose())
review = rev_by_rec.dot(rev_by_rec.transpose())
title = recipe_by_titles.dot(recipe_by_titles.transpose())
verb = recipe_by_verbs.dot(recipe_by_verbs.transpose())

# cursor.execute("DELETE FROM metadata")
# ratings_bytes = ratings.tostring()
# times_bytes = times.tostring()
# print np.fromstring(times_bytes).shape
# cursor.execute("INSERT INTO metadata (id, ratings, times) VALUES (0, %s, %s);", (psycopg2.Binary(ratings_bytes), psycopg2.Binary(times_bytes)))
# print "Inserted Metadata"
# conn.commit()

combined = 0.5 * (0.35*ingredient + 0.65*review) + 0.05*title + 0.05*verb

# test = 0.5 * (0.35*rec_svd.dot(rec_svd[5,:]) + 0.65*rev_by_rec.dot(rev_by_rec[5,:])) + 0.05*recipe_by_titles.dot(recipe_by_titles[5,:]) + 0.05*recipe_by_verbs.dot(recipe_by_verbs[5,:])

test = np.copy(combined[4491])
print test[:10]
print test.shape

# num_rec, _ = combined.shape
# for i in range(num_rec):
# 	bytes = combined[i].tostring()
# 	cursor.execute("INSERT INTO combined (id, scores) VALUES (%s, %s);", (i, psycopg2.Binary(bytes)))
# 	sys.stdout.write("\rInserted " + str(i))
# 	sys.stdout.flush()
# print ""
# print "Inserted Combined"
# conn.commit()

cursor.execute("SELECT scores FROM combined WHERE id = {}".format(4489))
score = np.fromstring(cursor.fetchone()[0])
print score[:10]
print score.shape
print "Select completed"

conn.close()
print "Connection closed"
