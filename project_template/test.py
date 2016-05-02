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
    try:
        query = str(i).lower()
    except UnicodeEncodeError:
        query = (i.encode('utf8')).lower()
    ranked_recipes = index_search(query, n_ings, ing_by_rec, idf, ing_to_index, norm, recipes)
   
    return ranked_recipes

def find_recipes2(i, rush, srName=''):
    # takes string of ingredients and/or recipes
    try:
        squery = ""
        query = str(i).lower()
        if srName:
            squery = str(srName)            
    except UnicodeEncodeError:
        query = (i.encode('utf8')).lower()
        if srName:
            squery = (srName.encode('utf8'))
    ranked_recipes = final_search(query, rush,srName)
   
    return ranked_recipes
