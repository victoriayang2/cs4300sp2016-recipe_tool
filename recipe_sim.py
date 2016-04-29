from __future__ import print_function
import numpy as np
import json
import glob 
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import math
from nltk.tokenize import TreebankWordTokenizer
%matplotlib inline

recipes = []
path = 'jsons/parsed*.json'   
files=glob.glob(path)   
for file in files: 
    with open(file) as f:
        for line in f:
            recipes.append(json.loads(line))

recipe_name_to_index = {name:i for i,name in enumerate(r['name'] for r in recipes)}
recipe_index_to_name = {i:name for name,i in recipe_name_to_index.iteritems()}
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
    coefficients.append(len(inter)/float(len(union)))
    #calculating shared verbs coefficient
    verbs1 = set(recipe_index_to_verbs[index1])
    verbs2 = set(recipe_index_to_verbs[index2])
    inter_verb = verbs1.intersection(verbs2)
    union_verb = verbs1.union(verbs2)
    coefficients.append(len(inter_verb)/float(len(union_verb)))
    #calculating shared ingredients coefficient
    ing1 = set(recipe_index_to_ing[index1])
    ing2 = set(recipe_index_to_ing[index2])
    inter_ing = ing1.intersection(ing2)
    union_ing = ing1.union(ing2)
    coefficients.append(len(inter_ing)/float(len(union_ing)))
    return coefficients   

def recipe_sim(a,b,c,recipes):
    """
    Input: 
    a: the weight for same title coefficient
    b: the weight for shared verbs coefficient
    c: the weight for shared ingredients coefficient
    a + b + c must equal 1
    Returns: a recipe-by-recipe similarity matrix
    """
    recipe_sims = np.empty([len(recipes), len(recipes)], dtype = np.float32)
    for i in range(len(recipes)):
        for j in range(len(recipes)):
            if i == j:
                recipe_sims[i][j] == 1
            else:
                name1 = recipe_index_to_name[i]
                name2 = recipe_index_to_name[j]
                coeff = recipe_comp(name1, name2)
                recipe_sims[i][j] = a*coeff[0] + b*coeff[1] + c*coeff[2]
    return recipe_sims                   