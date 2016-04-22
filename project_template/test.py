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

# Returns list of tuples (edit_distance,recipe) ordered by edit distance
def find_similar(q):
    transcripts = read_file(1)
    result = []
    for transcript in transcripts:
        m = transcript['name']
        result.append(((_edit(q, m)), transcript))
    return sorted(result, key=lambda tup: tup[0])

def find_recipes(i,r=''):
    # takes string of ingredients and/or recipes
    print len(recipes)
    return index_search(i, inverted_index, idf, norms, recipes)

# use both or have different modules to see which one is better
# return the resultant recipe list json that should be parsed

# if recipe(s) given compute similarity of recipe names using edit distance
    # if r != '':
    #     rec_list = r.split(",")
    #     recipes_r = [r for l in [find_similar(rec) for rec in rec_list] for r in l]
    #     recipes_r = [r[1] for r in sorted(recipes_r, key=lambda tup: tup[0])]

# if ingredient(s) given compute intersection of output of recipes from inverted index      
    # if i != '':
    #     ing_list = i.split(",")
    #     rec_ind = []
    #     for ing in ing_list:
    #         if ing in inverted_index:
    #             indices = inverted_index[ing]
    #             rec_ind.append(indices)
    #     common_indices = set.intersection(*map(set,rec_ind))
    #     recipes_i = [transcripts[i] for i in common_indices]

 # if both recipes and ingredients given, return intersection list of recipes sorted in order of edit distance     
    # if r !='' and i !='':
    #     ranked_recipes = [r for r in recipes_r for i in recipes_i if i['code']==r['code']]
      
    # if r == '':
    #     ranked_recipes = recipes_i
    
    # else:
    #     ranked_recipes = recipes_r
   
    # return ranked_recipes
