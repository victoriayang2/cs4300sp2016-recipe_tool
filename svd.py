from scipy import sparse, io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import numpy as np
import glob
import json
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def closest_ings(ing_in, k = 10):
    if ing_in not in ing_to_index: return "Not in vocab."
    sims = ing_compressed.dot(ing_compressed[ing_to_index[ing_in],:])
    asort = np.argsort(-sims)[:k+1]
    return [(index_to_ing[i],sims[i]/sims[asort[0]]) for i in asort[1:]]

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
            revs = rec.pop('reviews', []])
            tips = rec.pop('tips', []])
            docs.append({
            	'name': rec['name']
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
for d in docs:
	all_tips += d['tips']
	all_reviews += [rev['text'] for rev in d['reviews']]
# Create recipe vectors
vectorizer = TfidfVectorizer(binary=True)
rec_by_ing = vectorizer.fit_transform(all_ings)
ing_by_rec = sparse.csr_matrix.transpose(rec_by_ing)


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

print "Ing: {}".format(ing_compressed.shape)
print "Rec: {}".format(rec_compressed.shape)

ing_to_index = vectorizer.vocabulary_
index_to_ing = {i:t for t,i in ing_to_index.iteritems()}

ing_compressed = normalize(ing_compressed, axis = 1)

# closest_ings("query")

# from sklearn.manifold import TSNE
# tsne = TSNE(verbose=1)
# projected_recs = tsne.fit_transform(rec_compressed)
# plt.figure(figsize=(15,15))
# plt.scatter(projected_recs[:,0],projected_recs[:,1])
# plt.show()

rec_compressed = normalize(rec_compressed, axis = 1)
def closest_recs(rec_index_in, k = 5):
    sims = rec_compressed.dot(rec_compressed[rec_index_in,:])
    asort = np.argsort(-sims)[:k+1]
    return [(recipes[i]['name'],sims[i]/sims[asort[0]]) for i in asort[1:]]

for i in random.sample(range(len(recipes)), 10):
    print(recipes[i]['name'])
    for title, score in closest_recs(i):
        print("{}: {:.3f}".format(title[:40], score))
    print
