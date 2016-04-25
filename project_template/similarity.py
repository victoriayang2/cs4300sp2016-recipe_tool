from __future__ import print_function
#from .models import Chunks
import numpy as np
from scipy import sparse, io
import json
import glob
import math
import pickle
from collections import defaultdict

ing_by_rec = io.mmread("data/ing_by_rec.mtx").tocsr().toarray()

with open("data/idf.npy", "rb") as f:
    idf = np.load(f)

with open("data/ing_to_index.pickle", "rb") as f:
    ing_to_index = pickle.load(f)

with open("data/recipes.pickle", "rb") as f:
    recipes = pickle.load(f)

with open("data/norm.npy", "rb") as f:
    norm = np.load(f)

n_ing = len(ing_to_index)


def index_search(query, n_ing, ibr, idf, ing_to_index, norm, recipes):
    if query == "":
        return []
    else:
        results = defaultdict(float)
        q_vec = np.zeros([n_ing])
        query_toks = [q.strip() for q in query.split(",")]
        query_set = set(query_toks)
        # Construct query vector
        for q in query_toks:
            if q in ing_to_index:
                q_vec[ing_to_index[q]] = idf[ing_to_index[q]]
        # Normalize query vector with l2 norm
        q_norm = (q_vec * q_vec).sum()**0.5
        q_vec /= q_norm
        scores = q_vec.dot(ibr)
        denom = q_norm * norm
        scores /= denom[0]
        #sorting
        order = sorted(enumerate(scores.flat), key=lambda pair:pair[1], reverse=True)
        results = [recipes[o[0]] for o in order if o[1] > 0]
        for rec in results:
            rec['diff'] = ", ".join(list(set(rec['ing']) - query_set))
            rec['match'] = ", ".join(list(set(rec['ing']) & query_set))
        return results

# NUM_CHUNKS = 5
# recipes = []
# for i in range(1,NUM_CHUNKS+1):
#     path = Chunks.objects.get(id = i).address;
#     with open(path) as f:
#         for line in f:
#             r = json.loads(line)
#             r.pop('reviews', None)
#             recipes.append(r)

# path = 'jsons/parsed*.json'
# files=glob.glob(path)
# for file in files:
#     with open(file) as f:
#         for line in f:
#             r = json.loads(line)
#             r.pop('reviews', None)
#             recipes.append(r)

# # Sort recipes by name
# recipes.sort(key=lambda r:r['name'])

# # Dictionary of recipe name to recipe ingredients
# recipe_ingredients = {}
# # List of all ingredients
# all_ingredients = []

# for recipe in recipes:
#     recipe_ingredients[recipe['name']] = recipe['ing']
#     all_ingredients += recipe['ing']

# # Remove duplicates and sort ingredients to get indices
# all_ingredients = sorted(set(all_ingredients))

# id_to_name = {}


# #inverted index of ingredient to doc IDs
# inverted_index = defaultdict(list)
# for i, rec in enumerate(recipes):
#     for ing in rec['ing']:
#         inverted_index[ing].append(i)
            
# idf = {}
# for ing in inverted_index.keys():
#     num_docs = len(inverted_index[ing])
#     idf[ing] = math.log(len(recipes)/float(1+num_docs),2)
    
# norms = np.zeros(len(recipes))
# for ing in inverted_index:
#     ing_idf = idf[ing]
#     for doc in inverted_index[ing]:
#         norms[doc] += ing_idf**2
# norms = np.sqrt(norms)

# with open('./project_template/inverted_index.pickle','rb') as f:
#     inverted_index = pickle.load(f)
# with open('./project_template/idf.pickle','rb') as f:
#     idf = pickle.load(f)
# with open('./project_template/norms.pickle','rb') as f:
#     norms = pickle.load(f)
# with open('./project_template/recipes.pickle','rb') as f:
#     recipes = pickle.load(f)

#performs a search based on cosine similarity
# def index_search(query, index, idf, norms, recipes):
#     results = defaultdict(float)
#     query_toks = [q.strip() for q in query.split(",")]
#     query_set = set(query_toks)
#     norm_q = 0
#     for ing in query_toks:
#         if ing in index.keys():
#             norm_q += (idf[ing])**2
#             for doc in index[ing]:              
#                 score = idf[ing] * idf[ing]
#                 results[doc] += score
#     #normalizing
#     for doc in results:
#         results[doc] = results[doc]/(float(norms[doc])*(math.sqrt(norm_q)))
#     #sorting
#     results = sorted(results.items(), key=lambda x: x[1], reverse=True) 
#     results = map (lambda t: (t[1], t[0]), results)
#     new_results = []
#     for (score, doc_id) in results:
#         if score > 0:
#             rec = recipes[doc_id]
#             rec['diff'] = ", ".join(list(set(rec['ing']) - query_set))
#             new_results.append(rec)
            
#     return new_results
