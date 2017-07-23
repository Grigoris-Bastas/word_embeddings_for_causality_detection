#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from operator import itemgetter
import operator
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
import sys; sys.path.append('/home/irvin/Downloads/pattern-2.6')
from numpy import linalg as LA				

def read_sentence(File, M):
	L = []
	Negation = False
	for line in File:
		entry = line.split('\t')
		if line!='\n':
			L.append(entry)	
			if entry[2]=='ne':
				Negation = True
				neParent = int(entry[7])

		else:
			if Negation:
				L[neParent][2] = 'ne_' + L[neParent][2]
			break	
	for lu in L:
		M.append(lu[2])
		print lu[2],
	print

def cosine(a,b):
	return np.inner(a,b)/(LA.norm(a)*LA.norm(b))

def phrase_vector(Phrase, Vocabulary, Vectors): 
	Summ = [0 for i in Vectors[0]]
	Concat = []
	count = 0
	for w in Phrase:
		if w in Vocabulary:
			count+=1
#			print w.encode('utf-8'),
			i = Vocabulary.index(w)
			Summ = map(lambda x,y: x+y, Summ,Vectors[i])
			
	Avg = [x/count for x in Summ]		

	return (Avg, Summ)

def probablity(Phrase, VocabularyP, Answer, VocabularyA): 
	Summ = [0 for i in Vectors[0]]
	Concat = []
	count = 0
	for pw in filter(lambda w: (l in VocabularyP, Phrase)):
		for aw in filter(lambda w: (l in VocabularyP, Answer)):
			PMI += pmi(pw, aw)
			count+=1
	return avg =  PMI/count

#			print w.encode('utf-8'),
			i = Vocabulary.index(w)
			Summ = map(lambda x,y: x+y, Summ,Vectors[i])
			
	Avg = [x/count for x in Summ]		

	return (Avg, Summ)

def npmi(prob, index, string):
        global maxlen
        global cw2f
        global ci2f
        if index != 0:
                p_e = ei2f[index]/maxlen
                p_c = cw2f[string]/maxlen
                pmi = log(prob / p_e, 10)
                h = lambda x : -2*log(x,2)
                pconj = h(prob * p_c)
                npmi = pmi / pconj
                return npmi
        else:
                return 0

def count_freq(D, key):
	D = {}
	if key in D: D[key]+=1
	else: D[key]=1
		
if __name__ == "__main__":

	P[]
	A1=[]
	A2=[]
	Vocabulary = []
	VocabularyE = []
	Vectors = []
	VectorsC = []
	VectorsE = []
	TupleC = {}
	with open('./word2vecf_extractions/cause_vectors.txt','r', 'utf-8') as f: 
		next(f)
		for line in f:
			entry = deepcopy(line.split(' '))
			VocabularyE.append(entry[0])
			vector = map(float,entry[1:-1]) 
			VectorsC.append(vector)
				

	print pd.Series(VectorsE)


	cause = sys.argv[1]
	effet = sys.argv[2]
	#Causine = {}

	#print cosine(VectorsC[cause], VectorsE[effet.decode('utf8')])

	#print
	#print LA.norm(VectorsE[cause.decode('utf8')])
	#print

	#Causine = {key:np.inner(c,  VectorsE[key]) for key in VectorsE}

	#print Causine
	#print
	#for key, value in sorted(Causine.iteritems(), key=itemgetter(1), reverse=True)[0:40]:
	#	print key.encode('utf-8'), value

	#oooo


	xfile = open("./copa_conlled.txt", 'r', 'utf-8')
	tree = ET.parse('./copa-dev.fr.xml')
	root = tree.getroot()
	C = c = n = 0.0
	for item in root.findall('item'):
		i = int(item.get('id'))
		ask_for = item.get('ask-for')
		answer = item.get('most-plausible-alternative') 

		if ask_for == 'cause':
			VectorsP = VectorsE
			VectorsA = VectorsC
			VocabularyP = VocabularyE
			VocabularyA = VocabularyC
		else:
			VectorsP = VectorsC
			VectorsA = VectorsE
			VocabularyP = VocabularyC
			VocabularyA = VocabularyE

		read_sentence(xfile, P)
		read_sentence(xfile, A1)
		read_sentence(xfile, A2)

		print
		print '('+str(i)+')'
		print ' '.join(P).encode('utf-8')
		print "KEYWORDS :: ",
		#pVecA, pVecB = phrase_vector(P, VocabularyP, VectorsP)
		print 
		print
		print ' '.join(A1).encode('utf-8')
		print "KEYWORDS :: ",
		#a1VecA, a1VecB = phrase_vector(A1, VocabularyA, VectorsA)
		print
		print
		print ' '.join(A2).encode('utf-8')
		print "KEYWORDS :: ",
		#a2VecA, a2VecB = phrase_vector(A2, VocabularyA, VectorsA)

		probability(P, VocabularyP, A1, VocabularyA)
		probability(P, VocabularyP, A2, VocabularyA)
		
		print '\n'
		if cosine(pVecA,a1VecA) > cosine(pVecA,a2VecA):
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
		
		P=[]
		A1=[]
		A2=[]
		n += 1
		if i == 50:
			break

		
	xfile.close()
	print c/n

