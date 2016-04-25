from models import Chunks
import os
import Levenshtein
import json
from .similarity import *


def read_file(n):
    path = Chunks.objects.get(id = n).address;
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

def find_recipes(i,r=''):
    # takes string of ingredients and/or recipes
    ranked_recipes = index_search(i, n_ing, ing_by_rec, idf, ing_to_index, norm, recipes)
    #ranked_recipes = index_search(i, inverted_index, idf, norms, recipes)

    # use both or have different modules to see which one is better
    # return the resultant recipe list json that should be parsed

    # if recipe(s) given compute similarity of recipe names using edit distance
    # transcripts = read_file(1)

    # if r != '':
    #     rec_list = r.split(",")
    #     recipes_r = [r for l in [find_similar(rec,transcripts) for rec in rec_list] for r in l]
    #     recipes_r = [r[1] for r in sorted(recipes_r, key=lambda tup: tup[0])]

    # # if ingredient(s) given compute cosine similarity of recipes  
    # if i != '':
    #     recipes_i = index_search(i,inverted_index,idf,norms,transcripts)
     
    # if r !='' and i !='':
    #     r_ids = [i['code'] for i in recipes_i]
    #     intersect = [r['code'] for r in recipes_r[:500] if r['code'] in r_ids]
    #     ranked_recipes = [j for j in recipes_i if j['code'] in intersect]
      
    # if r == '':
    #     ranked_recipes = recipes_i
    
    # if i =='':
    #     ranked_recipes = recipes_r
   
    return ranked_recipes
