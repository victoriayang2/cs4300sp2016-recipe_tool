from models import Docs
import os
import Levenshtein
import json
from .similarity import *


def read_file(n):
	path = Docs.objects.get(id = n).address;
	file = open(path)
	transcripts = json.load(file)
	return transcripts

# Some of the recipe names contain non-unicode characters which throw errors 
# so must be checked before applying edit distance
def _edit(query, msg):
    try:
        query = str(query).lower()
    except UnicodeEncodeError:
        query = (query.encode('utf8')).lower()
    
    try:
        msg = str(msg).lower()
    except UnicodeEncodeError:
        msg = (msg.encode('utf8')).lower()
        
    return Levenshtein.distance(query, msg)

# Returns list of tuples (edit_distance,recipe) ordered by edit distance from input recipes
def find_similar(q,transcripts):
    result = []
    for transcript in transcripts:
        m = transcript['name']
        result.append(((_edit(q, m)), transcript))
    return sorted(result, key=lambda tup: tup[0])

# Returns list of tuples (cosine_similarty, recipe) ordered by cosine_similarity from input ingredients
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
        if score != 0:
            new_results.append(recipes[doc_id])
    return new_results

def find_recipes(i,r):
# takes string of ingredients and/or recipes

# use both or have different modules to see which one is better
# return the resultant recipe list json that should be parsed

# if recipe(s) given compute similarity of recipe names using edit distance
    transcripts = read_file(1)

    if r != '':
        rec_list = r.split(",")
        recipes_r = [r for l in [find_similar(rec,transcripts) for rec in rec_list] for r in l]
        recipes_r = [r[1] for r in sorted(recipes_r, key=lambda tup: tup[0])]

# if ingredient(s) given compute cosine similarity of recipes  
    if i != '':
        recipes_i = index_search(i,inverted_index,idf,norms,transcripts)
     
    if r !='' and i !='':
        #i_ids = [i['code'] for i in recipes_i]
        #ranked_recipes = [r for r in recipes_r if r['code'] in i_ids]
        ranked_recipes = recipes_i
      
    if r == '':
        ranked_recipes = recipes_i
    
    if i =='':
        ranked_recipes = recipes_r
   
    return ranked_recipes