from __future__ import print_function
import numpy as np
import json
import glob 
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
from nltk.tokenize import TreebankWordTokenizer


recipes = []
path = 'jsons/parsed*.json'   
files=glob.glob(path)   
for file in files: 
    with open(file) as f:
        for line in f:
            recipes.append(json.loads(line))

recipe_index_to_name = {i:name for i,name in enumerate(r['name'] for r in recipes)}
recipe_name_to_index = {name:i for i,name in recipe_index_to_name.iteritems()}
recipe_index_to_verbs = {i:verbs for i,verbs in enumerate(r['verbs'] for r in recipes)}
recipe_index_to_ing = {i:ing for i,ing in enumerate(r['ing'] for r in recipes)}
tokenizer = TreebankWordTokenizer()       

def recipe_comp(name1, name2):
    """ 
    Input: two recipe names
    Returns: a list of length 3 
    [same title coefficient, shared verbs (from recipe instructions) coefficient, 
    shared ingredients coefficient]
    """   
    coefficients = []
    index1 = recipe_name_to_index[name1]
    index2 = recipe_name_to_index[name2]
    #calculating title coefficient
    common_words = ['a', 'and', 'the', 'on', 'with', 'in', 's']
    toks_1 = set([w for w in tokenizer.tokenize(name1) if w not in common_words])
    toks_2 = set([w for w in tokenizer.tokenize(name2) if w not in common_words])
    inter = toks_1.intersection(toks_2)
    union = toks_1.union(toks_2)
    coefficients.append(len(inter)/float(len(union)+1))
    #calculating shared verbs coefficient
    verbs1 = set(recipe_index_to_verbs[index1])
    verbs2 = set(recipe_index_to_verbs[index2])
    inter_verb = verbs1.intersection(verbs2)
    union_verb = verbs1.union(verbs2)
    coefficients.append(len(inter_verb)/float(len(union_verb)+1))
    #calculating shared ingredients coefficient
    ing1 = set(recipe_index_to_ing[index1])
    ing2 = set(recipe_index_to_ing[index2])
    inter_ing = ing1.intersection(ing2)
    union_ing = ing1.union(ing2)
    coefficients.append(len(inter_ing)/float(len(union_ing)+1))
    return coefficients     

def title_sim(recipes):
    title_sims = np.empty([len(recipes), len(recipes)], dtype = np.float32)
    for i in range(len(recipes)):
        for j in range(i, len(recipes)):
            if i == j:
                title_sims[i][j] = 1
                title_sims[j][i] = 1
            else:
                name1 = recipe_index_to_name[i]
                name2 = recipe_index_to_name[j]
                coeff = recipe_comp(name1, name2)
                title_sims[i][j] = coeff[0]
                title_sims[j][i] = coeff[0]
    return title_sims 

def verb_sim(recipes):
    verb_sims = np.empty([len(recipes), len(recipes)], dtype = np.float32)
    for i in range(len(recipes)):
        for j in range(i, len(recipes)):
            if i == j:
                verb_sims[i][j] = 1
                verb_sims[j][i] = 1
            else:
                name1 = recipe_index_to_name[i]
                name2 = recipe_index_to_name[j]
                coeff = recipe_comp(name1, name2)
                verb_sims[i][j] = coeff[1]
                verb_sims[j][i] = coeff[1]
    return verb_sims

def ing_sim(recipes):
    ing_sims = np.empty([len(recipes), len(recipes)], dtype = np.float32)
    for i in range(len(recipes)):
        for j in range(i, len(recipes)):
            if i == j:
                ing_sims[i][j] = 1
                ing_sims[j][i] = 1
            else:
                name1 = recipe_index_to_name[i]
                name2 = recipe_index_to_name[j]
                coeff = recipe_comp(name1, name2)
                ing_sims[i][j] = coeff[2]
                ing_sims[j][i] = coeff[2]
    return ing_sims

if __name__ == "__main__":
	t = open('title_sim.npy', 'w')
	np.save(t,title_sim(recipes))
	t.close()
	#v = open('verb_sim.npy', 'w')
	#np.save(v,verb_sim(recipes))
	#v.close()
	#i = open('ing_sim.npy', 'w')
	#np.save(i,ing_sim(recipes))
	#i.close()




