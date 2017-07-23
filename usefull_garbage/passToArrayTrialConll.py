#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import numpy as np
import sys
import nltk
from nltk.corpus import PlaintextCorpusReader

with open('/home/irvin/Dropbox/Thesis/frwac_1134.parsed.marked') as fd:
	corpusString = fd.read()


stream = sys.stdin
line = stream.readline()
sentnum = 1
sentence = ''
linenum = 0



dtype = [('id', string), ('word',string), ('stem', string), ('POS', string), ('POSverbose', string), ('details',string), ('vertex', string), ('tag', string)]
#convert Conll as 2D list and structured and unstructured array
while line:
	if len(line)>1:
		b = True
		for i in range(0,9):
			corpusList[linenum][i] = word.split('\t')[i]

		corpusList[linenum][10] = sentnum	
	else:
		if b == True
			sentnum += sentnum	
			b = False

	linenum += linenum
	line = stream.readline()

sortedList = corpusList[:]
sortedList.sort(key=lambda X:x[1])

corpusArray = np.array(corpusList)#, dtype=dtype)
structuredArray = corpusArray.copy()
structuredArray.view(dtype=dtype)	#https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.view.html


#create a sorted array for all conll's (meaningfull) words
sortedArray = corpusArray.copy()
np.sort(sortedArray, order='word')	#https://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.sort.html

#search_word
def search_word(word,A,n,m)
	index = -1
	for i range(0,n)
		if A[i][1] == word:
			index = i
			break
	return index
#TODO: binary search, tagged search)

	 



while line:
	if len(line)>1:
		word = line.split()[1]
		pos = line.split()[4]
		if pos
