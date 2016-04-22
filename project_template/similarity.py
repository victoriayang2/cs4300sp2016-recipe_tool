from __future__ import print_function
from .models import Chunks
import numpy as np
import json
import glob
import math
import os
from django.conf import settings
from collections import defaultdict

recipes = []
path = Chunks.objects.get(id = 1).address;
with open(path) as f:
    for line in f:
        r = json.loads(line)
        r.pop('reviews', None)
        recipes.append(r)

# path = os.path.join(settings.PROJECT_ROOT, '/static/jsons/parsed*.json')
# print(path)
# files=glob.glob(path)   
# for file in files: 
#     with open(file) as f:
#         for line in f:
#             r = json.loads(line)
#             r.pop('reviews', None)
#             recipes.append(r)

# Sort recipes by name
recipes.sort(key=lambda r:r['name'])

# Dictionary of recipe name to recipe ingredients
recipe_ingredients = {}
# List of all ingredients
all_ingredients = []

for recipe in recipes:
    recipe_ingredients[recipe['name']] = recipe['ing']
    all_ingredients += recipe['ing']

# Remove duplicates and sort ingredients to get indices
all_ingredients = sorted(set(all_ingredients))

id_to_name = {}


#inverted index of ingredient to doc IDs
inverted_index = defaultdict(list)
for i, rec in enumerate(recipes):
    for ing in rec['ing']:
        inverted_index[ing].append(i)
            
idf = {}
for ing in inverted_index.keys():
    num_docs = len(inverted_index[ing])
    idf[ing] = math.log(len(recipes)/float(1+num_docs),2)
    
norms = np.zeros(len(recipes))
for i in range(len(recipes)):
    norm = 0
    for ing in inverted_index.keys():
        for doc in inverted_index[ing]:
            if i == doc:
                norm = norm + (idf[ing])**2
    norms[i] = math.sqrt(norm)

#performs a search based on cosine similarity
def index_search(query, index, idf, norms, recipes):
    results = {}
    query_toks = query.split(",")
    norm_q = 0
    for ing in query_toks:      
        if ing in index.keys():
            norm_q += (idf[ing])**2
            for doc in index[ing]:              
                score = idf[ing] * idf[ing]
                if doc in results.keys():
                    results[doc] = results[doc] + score
                else:
                    results[doc] = score
    #normalizing
    for doc in results:
        results[doc] = results[doc]/(float(norms[doc])*(math.sqrt(norm_q)))
    #sorting
    results = sorted(results.items(), key=lambda x: x[1], reverse=True) 
    results = map (lambda t: (t[1], t[0]), results)
    new_results = []
    for (score, doc_id) in results:
        if score == 0: 
            continue
        else:
            new_results.append(recipes[doc_id])
    
    return new_results