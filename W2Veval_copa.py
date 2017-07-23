#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import gensim
from gensim.models.keyedvectors import KeyedVectors
from operator import itemgetter
import operator
import pandas as pd
from codecs import open
import os
import numpy as np
import sys
import re
import xml.etree.ElementTree as ET
from numpy import linalg as LA				


class lu:
        def __init__(self, X, dist=None, word=None, lemma=None, pos1=None, pos2=None, synt=None, parent=None):
		self.id = int(X[0])
		self.word = X[1]
		self.lemma = X[2]
		self.pos1 = X[3]
		self.pos2 = X[4]
		self.parent = int(X[7])
		self.synt = X[8]
		self.dist = dist


def read_sentence(File, M, prefix):
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
				L[neParent-1][2] = 'ne_' + L[neParent-1][2]
			break	
	for i in range(0, len(L)):		
		L[i][2] = prefix + L[i][2]
	#	M.append(prefix+lu[2])
		M.append(lu(L[i]))

def cosine(a,b):
	return np.inner(a,b)/(LA.norm(a)*LA.norm(b))

def w2i(w):
	return model.wv.index2word.index(w.encode('utf-8'))

def sentence_vector(Phrase, Vocabulary, Vectors): 
	Summ = [0 for i in Vectors[0]]
	Phrase = [x.lemma for x in Phrase]
	Concat = []
	Keywords = []
	count = 0
	for w in filter((lambda w: w.encode('utf-8') in Vocabulary), Phrase) :
		wi = model.wv.index2word.index(w.encode('utf-8'))
		Summ = map(lambda x,y: x+y, Summ, Vectors[wi])
		Keywords.append(w)
		count+=1
	Avg = [x/count for x in Summ]		
	return Avg, Keywords

def dot_method(Phrase, Answer, pVec, aVec):
        global Vocabulary
        global ask_for
        count = num = sumDot = sumBest = 0
	bestPair = ('None', 'None')
	maxDot = -10
	aKeywords = []
	pKeywords = []

	constraints = lambda w: ((w.lemma.encode('utf-8') in Vocabulary) and 
		#		(w.synt in ['suj', 'obj', 'root']) and 
				(w.lemma[3:] not in ['fille','femme', 'homme','enfant']))

	for aw in filter(constraints, Answer):
		aKeywords.append(aw.lemma)

        for pw in filter(constraints, Phrase):
		bestMatch = -100
		num += 1
                for aw in filter(constraints, Answer):
			
			if pw.lemma[3:] == aw.lemma[3:]:
				continue
			p = pVec[w2i(pw.lemma)]
			a = aVec[w2i(aw.lemma)]
			sumDot += np.inner(p, a)	
			print '   ', pw.lemma.encode('utf-8'), aw.lemma.encode('utf-8'), np.inner(p, a)
			maxDot = max(maxDot, np.inner(p, a))
			index, bestMatch = max(enumerate((bestMatch, np.inner(p,a))), key = lambda x: x[1])
			bestPair = (pw.lemma, aw.lemma) if index else bestPair
			count+=1

		sumBest += bestMatch	
		if sys.argv[1]=='best':
			print '    -------------------------------->',' '.join(bestPair)
		pKeywords.append(pw.lemma)
	avgDot = sumDot/count if count!=0 else None
	avgBest = sumBest/num if count!=0 else None
	return (avgBest, avgDot, maxDot, pKeywords, aKeywords)

def compare(pa1, pa2):
	global c
	print pa1, pa2, abs(pa1-pa2)
	if pa1 > pa2:
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

def count_freq(D, key):
	if key in D: D[key]+=1
	else: D[key]=1
		
if __name__ == "__main__":

	P=[]
	A1=[]
	A2=[]
	fname = '/home/irvin/python_practice_thesis/thesisBigData/cs-ef_vectors_23_allFR'
	model = gensim.models.Word2Vec.load(fname)
	WordVec = model.wv.syn0
	print WordVec.shape
	ContVec = model.syn1neg
	print ContVec.shape
	Vocabulary = list(model.wv.vocab.keys())

	xfile = open("./copa/copa_conlled.txt", 'r', 'utf-8')
	tree = ET.parse('./copa/copa-dev.fr.xml')
	root = tree.getroot()
	C = c = n = 0.0
	for item in root.findall('item'):
		i = int(item.get('id'))
		ask_for = item.get('asks-for')
		answer = item.get('most-plausible-alternative') 

		if ask_for == 'cause':
			read_sentence(xfile, P, 'ef_')
			read_sentence(xfile, A1, 'cs_')
			read_sentence(xfile, A2, 'cs_')
		elif ask_for == 'effect':	
			read_sentence(xfile, P, 'cs_')
			read_sentence(xfile, A1, 'ef_')
			read_sentence(xfile, A2, 'ef_')

		if i == 10:
			continue
		
		if sys.argv[1] == 'sentence':
			print
			print '('+str(i)+')'
			print ' '.join(map(lambda x: x.lemma[3:], P)).encode('utf-8')
			pVec, pKeywords = sentence_vector(P, Vocabulary, WordVec)
			print "KEYWORDS :: ", ' '.join([x[3:] for x in pKeywords]).encode('utf-8')
			print
			print ' '.join(map(lambda x: x.lemma[3:], A1)).encode('utf-8')
			a1Vec, a1Keywords = sentence_vector(A1, Vocabulary, ContVec)
			print "KEYWORDS :: ", ' '.join([x[3:] for x in a1Keywords]).encode('utf-8')
			print "SIMILARITY ::", np.inner(pVec,a1Vec).encode('utf-8')
			print
			print ' '.join(map(lambda x: x.lemma[3:], A2)).encode('utf-8')
			a2Vec, a2Keywords = sentence_vector(A2, Vocabulary, ContVec)
			print "KEYWORDS :: ", ' '.join([x[3:] for x in a2Keywords]).encode('utf-8') 
			print "SIMILARITY ::", np.inner(pVec,a2Vec).encode('utf-8')
			print '\n'
			compare(np.inner(pVec,a1Vec), np.inner(pVec,a2Vec))
		else:
			print '______________________________________________________________________________________________'
			print
			print '('+str(i)+')'
			print ' '.join(map(lambda x: x.word, P)).encode('utf-8')
			print
			print ' '.join(map(lambda x: x.word, A1)).encode('utf-8')
			print
			print ' '.join(map(lambda x: x.word, A2)).encode('utf-8')
			print
			print 'P-A1'
			avgBestSim_1, avgDotSim_1, maxDotSim_1, pKeywords, a1Keywords = dot_method(P, A1, WordVec, ContVec)
			print
			print "p__KEYWORDS :: ", ' '.join([x[3:] for x in pKeywords]).encode('utf-8')
			print "a1_KEYWORDS :: ", ' '.join([x[3:] for x in a1Keywords]).encode('utf-8')
			print
			print 'P-A2'
			avgBestSim_2, avgDotSim_2, maxDotSim_2, pKeywords, a2Keywords = dot_method(P, A2, WordVec, ContVec)
			print
			print "a2_KEYWORDS :: ", ' '.join([x[3:] for x in a2Keywords]).encode('utf-8')
			print
			
			if (avgDotSim_1 and avgDotSim_2):	#at least one word found in each sentence
				
				if sys.argv[1] == 'avg':
					compare(avgDotSim_1, avgDotSim_2)
				elif sys.argv[1] == 'max':
					compare(maxDotSim_1, maxDotSim_2)
				elif sys.argv[1] == 'best':
					compare(avgBestSim_1, avgBestSim_2)
			else:
				n-=1
			

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

