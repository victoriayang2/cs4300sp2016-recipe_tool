from __future__ import print_function
import numpy as np
import json
import glob 
import numpy as np

recipes = []
path = 'jsons/parsed*.json'   
files=glob.glob(path)   
for file in files: 
    with open(file) as f:
        for line in f:
            recipes.append(json.loads(line))

#dictionary of recipe name to recipe ingredients
recipe_ingredients = {}
for recipe in recipes:
    recipe_ingredients[recipe['name']] = recipe['ing']

id_to_name = {}


#inverted index of ingredient to doc IDs
inverted_index = {}
for i in range(len(recipes)):
    for ing in recipes[i]['ing']:
        if ing in inverted_index:
            recipe_indices = [x for x in inverted_index[ing]]
            if i in recipe_indices:
                continue
            else:
                inverted_index[ing].append(i)
        else:
            inverted_index[ing]=[i]
            
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
        if ing not in index.keys():
            continue
        else:
            norm_q = norm_q + (idf[ing])**2
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
        new_results.append(recipes[doc_id])
    
    return new_results[0:9]