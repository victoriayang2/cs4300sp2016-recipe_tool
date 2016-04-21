from .models import Docs
import os
import Levenshtein
import json


def read_file(n):
	path = Docs.objects.get(id = n).address;
	file = open(path)
	transcripts = json.load(file)
	return transcripts

def _edit(query, msg):
    return Levenshtein.distance(query.lower(), msg.lower())

def find_similar(q):
	transcripts = read_file(1)
	result = []
	for transcript in transcripts:
		for item in transcript:
			m = item['text']
			result.append(((_edit(q, m)), m))

	return sorted(result, key=lambda tup: tup[0])

def find_recipes(i,r):
	print i
	print r
	#split i and r based on , 
	# compute the similarity on names using edit distance
	# compute the resultant of recipes based on intersection of output of recipes from inverted index
	# use both or have different modules to see which one is better
	# return the resultant recipe list json that should be parsed