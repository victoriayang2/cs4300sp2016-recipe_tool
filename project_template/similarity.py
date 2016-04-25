import numpy as np
from scipy import sparse, io
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
