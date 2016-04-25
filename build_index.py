import numpy as np
from scipy import sparse, io
import json
import glob
import pickle
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer

def custom_tokenizer(ings):
    by_comma = ings.split(',')
    by_space = []
    for ing in by_comma:
        by_space += ing.split(' ')
    return by_space + by_comma

# recipes = []

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
# # List of ingredient list for each recipe
# all_ings = [",".join(rec['ing']) for rec in recipes]
# # Create recipe vectors
# tfidf_vec = TfidfVectorizer(binary=True, norm='l2', tokenizer=custom_tokenizer)
# rec_by_ing = tfidf_vec.fit_transform(all_ings)
# ing_by_rec = sparse.csr_matrix.transpose(rec_by_ing)
# idf = tfidf_vec.idf_
# n_rec, n_ing = rec_by_ing.shape
# ing_to_index = {v:i for i, v in enumerate(tfidf_vec.get_feature_names())}

ing_by_rec = io.mmread("./ing_by_rec.mtx").tocsr().toarray()

with open("./idf.npy", "rb") as f:
    idf = np.load(f)

with open("./ing_to_index.pickle", "rb") as f:
    ing_to_index = pickle.load(f)

with open("./recipes.pickle", "rb") as f:
    recipes = pickle.load(f)

with open("./norm.npy", "rb") as f:
    norm = np.load(f)

n_ing = len(ing_to_index)

# norm = np.sqrt(rec_by_ing.multiply(rec_by_ing).sum(axis=1)).flatten()

# with open("./norm.npy", "wb") as f:
#     np.save(f, norm)

# io.mmwrite("./ing_by_rec.mtx", ing_by_rec)

# with open("./idf.npy", "wb") as f:
#     np.save(f, idf)

# with open("./ing_to_index.pickle", "wb") as f:
#     pickle.dump(ing_to_index, f)

# with open("./recipes.pickle", "wb") as f:
#     pickle.dump(recipes, f)

#performs a search based on cosine similarity
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

test_query = "soy sauce,butter"
test_results = index_search(test_query, n_ing, ing_by_rec, idf, ing_to_index, norm, recipes)
print(test_results[0]['match'])

