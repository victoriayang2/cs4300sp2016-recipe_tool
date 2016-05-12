from models import Combined, Metadata
import numpy as np
from scipy import sparse, io
import pickle
from collections import defaultdict
import Levenshtein
import nltk
from nltk.stem.wordnet import *
import json
import glob

# Point nltk to local corpus
nltk.data.path.append('./nltk_data/')

# Lemmatizer
wnl = WordNetLemmatizer()

# Ingredient Rows x Recipe Columns
ing_by_rec = io.mmread("data/ing_by_rec_final.mtx").tocsr().toarray()

with open("data/idf_final.npy", "rb") as f:
    idf = np.load(f)

with open("data/ing_to_index_final.pickle", "r") as f:
    ing_to_index = pickle.load(f)

with open("data/recipes.pickle", "r") as f:
    recipes = pickle.load(f)

with open("data/norm_final.npy", "rb") as f:
    norm = np.load(f)

n_ings = len(ing_to_index)


recipe_index_to_name = {i:name for i,name in enumerate(r['name'] for r in recipes)}
recipe_name_to_index = {name:i for i,name in recipe_index_to_name.iteritems()}


def findRecipeIndex(name):
    if name in recipe_name_to_index:  
        return recipe_name_to_index[name]
    else:
        return ""

def distanceMeasure(query, msg):
    try:
        query = str(query).lower()
    except UnicodeEncodeError:
        query = (query.encode('utf8')).lower()
    
    try:
        msg = str(msg).lower()
    except UnicodeEncodeError:
        msg = (msg.encode('utf8')).lower()
        
    return Levenshtein.distance(query, msg)


def findMostSimilar(i,ingList):
    result = []
    for ing in ingList:        
        result.append(((distanceMeasure(i, ing)), ing))
    return sorted(result, key=lambda tup: tup[0])

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
            matchedIngs = set()
            recIngList = list(set(rec['ing']))
            for ing in query_set:
                matchingIngs = [recipeIng for recipeIng in recIngList if ing in recipeIng.lower()]
                if len(matchingIngs)>0:
                    score,toUseIng = findMostSimilar(ing,matchingIngs)[0]
                    matchedIngs.add(toUseIng)                
            rec['diff'] = ", ".join(list(set(rec['ing']) - matchedIngs))
            rec['match'] = ", ".join(list(set(rec['ing']) & matchedIngs))
        return results


# Search to use in final app that accounts for match score
def final_search(query, reqIng, rush, srName):    
    if query == "":
        return []
    else:        
        results = defaultdict(float)
        q_vec = np.zeros([n_ings])
        query_toks = [" ".join([wnl.lemmatize(w) for w in q.split(" ")]) for q in query.split(",")]
        # Use the reqIng to double idf score of ingredients
        if not reqIng == "":
            reqIng = [int(i)*4+1 for i in reqIng.split(",")]
        else:
            reqIng = [1] * len(query_toks)
        query_matches = []
        # Construct query vector
        for i,q in enumerate(query_toks):
            if q in ing_to_index:
                q_vec[ing_to_index[q]] = reqIng[i] * idf[ing_to_index[q]]
                query_matches.append(q)
            # else:
            matching_ings = [recipeIng for recipeIng in ing_to_index.keys() if q in recipeIng.lower()]
            if len(matching_ings) > 0:
                matching_scores = findMostSimilar(q,matching_ings)
                for s, m in matching_scores:
                    if s <= 15:
                        query_matches.append(m)
                        q_vec[ing_to_index[m]] = reqIng[i] * idf[ing_to_index[m]]
        query_set = set(query_matches)
        # Normalize query vector with l2 norm
        q_norm = (q_vec * q_vec).sum()**0.5
        q_vec /= q_norm
        scores = q_vec.dot(ing_by_rec)
        denom = q_norm * norm
        scores /= denom[0]
        scores /= np.max(scores)
        #add match_score to cosine score
        bin_rec_vecs = ing_by_rec.copy()
        bin_rec_vecs[bin_rec_vecs > 0] = 1
        # Binary query vector
        q_vec[q_vec > 0] = 1
        ing_counts = np.atleast_2d(q_vec).transpose() + bin_rec_vecs
        ing_counts[ing_counts > 1] = 1
        denom = np.sum(ing_counts, axis=0).astype(np.float32)
        # Multiply query vector down each recipe column
        match_counts = q_vec.reshape(n_ings,1) * bin_rec_vecs
        # Sum along columns to get match count
        match_counts = np.sum(match_counts, axis=0)
        # Match score is ratio of matches to total ingredients in recipe
        match_scores = match_counts / denom
        match_scores /= np.max(match_scores)

        # SVD similarity scores given specified recipe
        svd_scores=[]
        verb_scores=[]
        title_scores=[]
        if srName:
            rec_index_in = findRecipeIndex(srName) + 1
            svd_score = np.fromstring(Combined.objects.get(id = rec_index_in).scores)

        # Weighted average of our different scores calculated here
        ratings = np.fromstring(Metadata.objects.get(id = 1).ratings)
        if rush:
            times = np.fromstring(Metadata.objects.get(id = 1).times)
            combined_scores = .6*scores + .25*match_scores  + .05*ratings + .1*times
        else:
            combined_scores = .7*scores + .25*match_scores + .05*ratings
        if srName:
            combined_scores = .4*combined_scores + svd_score
        #sorting
        order = sorted(enumerate(combined_scores.flat), key=lambda pair:pair[1], reverse=True)
        results = [recipes[o[0]] for o in order if o[1] > 0.25]
        for i,rec in enumerate(results):
            rec['diff'] = ", ".join(list(set(rec['ing']) - query_set))
            rec['match'] = ", ".join(list(set(rec['ing']) & query_set))
            rec['score'] = order[i][1]
        return results

