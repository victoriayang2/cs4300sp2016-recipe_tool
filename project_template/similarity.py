import numpy as np
from scipy import sparse, io
import pickle
from collections import defaultdict
import Levenshtein
from nltk.stem.wordnet import *
import time

start = time.time()
# Lemmatizer
wnl = WordNetLemmatizer()

# Ingredient Rows x Recipe Columns
ing_by_rec = io.mmread("data/ing_by_rec_final.mtx").tocsr().toarray()

# Ingredient Rows x Ingredient Columns
ing_coccur = io.mmread("data/ing_cooccur.mtx").tocsr().toarray()

with open("data/idf_final.npy", "r") as f:
    idf = np.load(f)

with open("data/ing_to_index_final.pickle", "r") as f:
    ing_to_index = pickle.load(f)

with open("data/recipes.pickle", "r") as f:
    recipes = pickle.load(f)

with open("data/norm_final.npy", "r") as f:
    norm = np.load(f)

with open("data/ratings.npy", "r") as f:
    ratings = np.load(f)

with open("data/times.npy", "r") as f:
    times = np.load(f)

with open("data/rec_svd_normalized.npy", "r") as f:
    rec_svd = np.load(f)

n_ings = len(ing_to_index)

print "Setup Time: {}".format(time.time() - start)


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
def final_search(query, rush):
    if query == "":
        return []
    else:
        results = defaultdict(float)
        q_vec = np.zeros([n_ings])
        query_toks = [" ".join([wnl.lemmatize(w) for w in q.split(" ")]) for q in query.split(",")]
        query_set = set(query_toks)
        ### Debug
        start = time.time()
        ###
        # Construct query vector
        for q in query_toks:
            if q in ing_to_index:
                q_vec[ing_to_index[q]] = idf[ing_to_index[q]]  
        ### Debug
        print "Qvec Time: {}".format(time.time() - start)
        ###
        ### Debug
        start = time.time()
        ###
        # Normalize query vector with l2 norm
        q_norm = (q_vec * q_vec).sum()**0.5
        q_vec /= q_norm
        scores = q_vec.dot(ing_by_rec)
        denom = q_norm * norm
        scores /= denom[0]
        ### Debug
        print "Calculate Score Time: {}".format(time.time() - start)
        ###
        ### Debug
        start = time.time()
        ###
        #add match_score to cosine score
        bin_rec_vecs = ing_by_rec.copy()
        bin_rec_vecs[bin_rec_vecs > 0] = 1
        # Shape: (4693,)
        ing_counts = np.sum(bin_rec_vecs, axis=0).astype(np.float32)
        print "ing_counts shape: {}".format(ing_counts.shape)
        # Binary query vector
        q_vec[q_vec > 0] = 1
        print "Qvec shape: {}".format(q_vec.shape)
        # Multiply query vector down each recipe column
        match_counts = q_vec.reshape(n_ings,1) * bin_rec_vecs
        print "match_counts (multiply) shape: {}".format(match_counts.shape)
        # Sum along columns to get match count
        match_counts = np.sum(match_counts, axis=0)
        print "match_counts (summed) shape: {}".format(match_counts.shape)
        # Match score is ratio of matches to total ingredients in recipe
        match_scores = match_counts / ing_counts
        print "match_scores shape: {}".format(match_scores.shape)
        # match_scores = []
        # for r in recipes:
        #     total_ings = len(r['ing'])
        #     match_ings = len([ing for ing in query_set if ing in r['ing']])
        #     match_scores.append(match_ings/total_ings)
        # match_scores = np.array(match_scores)

        # SVD similarity scores given specified recipe
        #svd_scores = rec_svd.dot(rec_svd[rec_index_in,:])

        # Weighted average of our different scores calculated here
        if rush:
            combined_scores = .7*scores + .2*match_scores + .05*times + .05*ratings
        else:
            combined_scores = .7*scores + .2*match_scores + .1*ratings
        ### Debug
        print "Combine Score Calc: {}".format(time.time() - start)
        ###
        ### Debug
        start = time.time()
        ###
        #sorting
        order = sorted(enumerate(combined_scores.flat), key=lambda pair:pair[1], reverse=True)
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
        ### Debug
        print "Sorting: {}".format(time.time() - start)
        ###
        return results

# test = final_search("chicken,onion")[:10]
# for t in test:
#     print t['name']

