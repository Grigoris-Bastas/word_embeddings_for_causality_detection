from copy import deepcopy
import pandas as pd
from codecs import open
import os
import numpy as np
import sys
import nltk
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import PlaintextCorpusReader
import re
import xml.etree.ElementTree as ET
from numpy import linalg as LA


def read_sentence(File, M):
	for line in File:
		if line=='\n':
			break
		entry = line.split(' ')
		M.append(entry[1])
		

def cosine(a,b):
	return np.inner(a,b)/(LA.norm(a)*LA.norm(b))

def phrase_vector(Phrase, Vocabulary, Vectors): 
	Summ = [0 for i in Vectors[0]]
	Concat = []
	for w in Phrase:
		if w in Vocabulary:
			print w.encode('utf-8'),
			i = Vocabulary.index(w)
			Summ = map(lambda x,y: x+y, Summ,Vectors[i])
			Concat = Concat + Vectors[i]

	return (Summ, Concat)

P=[]
A1=[]
A2=[]
Vocabulary = []
Vectors = []
with open('./dim200vecs','r', 'utf-8') as f: 
	next(f)
	for line in f:
		entry = deepcopy(line.split(' '))
		Vocabulary.append(entry[0])
		vector = map(float,entry[1:-1]) 
		Vectors.append(vector)

xfile = open("./lemmatized_copa.txt", 'r', 'utf-8')
tree = ET.parse('./copa-dev.fr.xml')
root = tree.getroot()
C = c = n = 0.0
for item in root.findall('item'):
	i = int(item.get('id'))
	ask_for = item.get('ask-for')
	answer = item.get('most-plausible-alternative') 

	read_sentence(xfile, P)
	read_sentence(xfile, A1)
	read_sentence(xfile, A2)

	print
	print '('+str(i)+')'
	print ' '.join(P).encode('utf-8')
	print "KEYWORDS :: ",
	pVecA, pVecB = phrase_vector(P, Vocabulary, Vectors)
	print 
	print
	print ' '.join(A1).encode('utf-8')
	print "KEYWORDS :: ",
	a1VecA, a1VecB = phrase_vector(A1, Vocabulary, Vectors)
	print
	print
	print ' '.join(A2).encode('utf-8')
	print "KEYWORDS :: ",
	a2VecA, a2VecB = phrase_vector(A2, Vocabulary, Vectors)
	
	print '\n'
	if cosine(pVecA,a1VecA) < cosine(pVecA,a2VecA):
		print ('1'==answer)
		if ('1'==answer):
			print 'correct: 1'
			c += 1
		else:
			print 'correct: 2'
	else:
		print ('2'==answer)
		if ('2'==answer):
			print 'correct: 2'
			c += 1
		else:
			print 'correct: 1'

	print
	print

#		if cosine(pVecB,a1VecB) < cosine(pVecB,a2VecB):
#			if ('1'==answer):
#				C += 1
#			if ('2'==answer):
#				C += 1
	
	P=[]
	A1=[]
	A2=[]
	n += 1
	if i == 50:
		break

	print 1-cosine([3,4],[5,6])	
	
xfile.close()
print c/n


