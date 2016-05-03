from scipy import sparse, io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import numpy as np
import glob
import json
import random
from scipy.stats import t
from numpy import average, std
from math import sqrt
#import nltk
#from nltk.stem.wordnet import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt




# returns confidence interval of mean
def confIntMean(a, conf=0.95):
	mean = average(a)
	t_bounds = t.interval(conf,len(a)-1)
	stddev = std(a,ddof=1)
	ci=[mean+critval*stddev/sqrt(len(a)) for critval in t_bounds]
	return ci
  	#mean, sem, m = np.mean(a), st.sem(a), st.t.ppf((1+conf)/2.0, len(a)-1)
  	

def custom_tokenizer(ings):
	return ings.split(",")

def closest_ings(ing_in, k = 10):
	if ing_in not in ing_to_index: return [("Not in vocab", 0)]
	sims = ing_compressed.dot(ing_compressed[ing_to_index[ing_in],:])
	asort = np.argsort(-sims)[:k+1]
	return [(index_to_ing[i],sims[i]/sims[asort[0]]) for i in asort[1:]]

def closest_recs(rec_index_in, k = 5):
	sims = rec_compressed.dot(rec_compressed[rec_index_in,:])
	asort = np.argsort(-sims)[:k+1]
	return [(recipes[i]['name'],sims[i]/sims[asort[0]]) for i in asort[1:]]

def closest_recs_by_review(rec_index_in, k = 10):
	sims = rev_rec_compressed.dot(rev_rec_compressed[rec_index_in,:])
	asort = np.argsort(-sims)[:k+1]
	return [(recipes[i]['name'],sims[i]/sims[asort[0]]) for i in asort[1:]]

def cooccur_ings(ing_in, k=10):
	if ing_in not in ing_to_index: return [("Not in vocab", 0)]
	index = ing_to_index[ing_in]
	sims = ing_cooccur[index]
	sims[index] = 0
	asort = np.argsort(-sims)[:k]
	return [(index_to_ing[i],sims[i]) for i in asort]

# All recipes, sans reviews
recipes = []
# All recipes, with only reviews and tips
docs = []

path = 'jsons/parsed*.json'
files=glob.glob(path)
for file in files:
    with open(file) as f:
        for line in f:
            rec = json.loads(line)
            revs = rec.pop('reviews', [])
            tips = rec.pop('tips', [])
            docs.append({
            	'name': rec['name'],
            	'reviews': revs,
            	'tips': tips
            	})
            recipes.append(rec)

# Sort recipes by name
recipes.sort(key=lambda r:r['name'])
# Sort docs by recipe name
docs.sort(key=lambda d:d['name'])
# List of ingredient list for each recipe
all_ings = [",".join(rec['ing']) for rec in recipes]
# List of all tips
all_tips = []
# List of all reviews
all_reviews = []
all_ratings = []
for d in docs:
	all_tips += d['tips']	
	all_reviews.append(".".join([rev['text'] for rev in d['reviews']]))
	all_ratings.append([rev['rating'] for rev in d['reviews']])

rcis = []
wrci = []
for ratingList in all_ratings:
	ci = confIntMean(ratingList)
	rcis.append(ci[1]-ci[0])

for rci in rcis:
	count=0.0
	for i in rcis:
		if i>rci:
			count+=1
	wrci.append(count/len(rcis))

wrci = np.array(wrci)

# Create recipe vectors by review text
# rev_vectorizer = TfidfVectorizer(stop_words='english', min_df=75, max_df=0.7)
# rec_by_review = rev_vectorizer.fit_transform(all_reviews)
# review_by_rec = sparse.csr_matrix.transpose(rec_by_review)

# # print review_by_rec.shape #6965, 4693

# # Decompose ingredient_by_recipe matrix
# rev_words_compressed, _, rev_rec_compressed = sparse.linalg.svds(review_by_rec, k=40)
# rev_rec_compressed = rev_rec_compressed.transpose()

# # print "Ing: {}".format(ing_compressed.shape)
# # print "Rec: {}".format(rec_compressed.shape)

# rev_rec_compressed = normalize(rev_rec_compressed, axis = 1)
with open("./data/rev_rec_compressed.npy", "r") as f:
	rev_rec_compressed = np.load(f)
	#np.save(f, rev_rec_compressed)
'''
Recipe similarity by review text
'''
for i in random.sample(range(len(recipes)), 10):
    print(recipes[i]['name'])
    for title, score in closest_recs_by_review(i):
        print("{}: {:.3f}".format(title[:40].encode("ascii", "ignore"), score))
    print

# noun_tags = ['NNS', 'NN', 'NNP', 'NNPS']

# verbs = [",".join(rec['verbs']) for rec in recipes]
# for v in verbs:
# 	#tag and print nouns
# 	tokens = v.split(',')
# 	pos_tags = nltk.pos_tag(tokens)
# 	for pt in pos_tags:
# 		if pt[1] in noun_tags:
# 			print pt[0]

# List of recipe times
times = np.array([r['time'] for r in recipes])
times[times < 1] = 1
times = np.log(times)
# print np.max(times) # 0.0
# print np.min(times) # -9.584
# Normalize by max
times /= np.max(times)
# Invert because longer time equates to lower ranking
times *= -1
# with open("./times.npy", "w") as f:
#     np.save(f, times)

# List of recipe ratings
ratings = np.array([r['rating'] for r in recipes])
#popularities = np.array([r['num_reviews'] for r in recipes])
#popularities[popularities > 5000] = 5000
#popularities[popularities < 50] = 1
#popularities = np.log(popularities)
#print np.max(popularities) # 8.517
#print np.min(popularities) # 0.0
# Scale by max to range from 0 to 1
#popularities /= np.max(popularities)
# Use popularity array to weight the ratings
#ratings *= popularities
# Normalize by max
#ratings /= np.max(ratings)
# print ratings.shape
ratings = np.multiply(ratings,wrci)
with open("./data/ratings.npy", "w") as f:
	np.save(f, ratings)

# Create recipe vectors
vectorizer = TfidfVectorizer(binary=True, norm=None, use_idf=False, smooth_idf=False, tokenizer=custom_tokenizer)
rec_by_ing = vectorizer.fit_transform(all_ings)
ing_by_rec = sparse.csr_matrix.transpose(rec_by_ing)

ing_to_index = vectorizer.vocabulary_
index_to_ing = {i:t for t,i in ing_to_index.iteritems()}

# 1429 x 1429
ing_cooccur = ing_by_rec.dot(rec_by_ing)
#io.mmwrite("./ing_cooccur.mtx", ing_cooccur)
#ing_cooccur = ing_cooccur.toarray()

# for i in cooccur_ings("chicken"):
# 	print "{}: {}".format(i[0], i[1])

# Decompose ingredient_by_recipe matrix
# u, s, v_trans = sparse.linalg.svds(ing_by_rec, k=100)

# print "U: {}".format(u.shape)
# print "S: {}".format(s.shape)
# print "Vt: {}".format(v_trans.shape)

# plt.plot(s[::-1])
# plt.xlabel("Singular value number")
# plt.ylabel("Singular value")
# plt.show()

ing_compressed, _, rec_compressed = sparse.linalg.svds(ing_by_rec, k=40)
rec_compressed = rec_compressed.transpose()

# print "Ing: {}".format(ing_compressed.shape)
# print "Rec: {}".format(rec_compressed.shape)

ing_compressed = normalize(ing_compressed, axis = 1)

# for ing in closest_ings("pepper"):
# 	print ing

# from sklearn.manifold import TSNE
# tsne = TSNE(verbose=1)
# projected_recs = tsne.fit_transform(rec_compressed)
# plt.figure(figsize=(15,15))
# plt.scatter(projected_recs[:,0],projected_recs[:,1])
# plt.show()

'''
Recipe Similarity
'''

rec_compressed = normalize(rec_compressed, axis = 1)
#with open("./data/rec_svd_normalized.npy", "w") as f:
 #   np.save(f, rec_compressed)

# closest_recs(0)

# for i in random.sample(range(len(recipes)), 10):
#     print(recipes[i]['name'])
#     for title, score in closest_recs(i):
#         print("{}: {:.3f}".format(title[:40], score))
#     print
