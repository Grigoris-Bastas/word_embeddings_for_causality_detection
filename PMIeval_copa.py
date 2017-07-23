#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
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


def bin_search(L, target):
        min = 0
        max = len(L) - 1
        while min <= max:
                avg = (min+max)//2
                if L[avg] > target:
                        max =  avg-1
                elif L[avg] < target:
                        min = avg+1
                else:
                        return True
        return False


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

def probability(Phrase, Answer): 
	global VocabP
	global VocabA
	global ask_for
	count = PMI = 0
	for pw in filter(lambda w: (w in VocabP), Phrase):
		for aw in filter(lambda w: (w in VocabA), Answer):
			if ask_for=='cause' and (aw+' '+pw in Tuples):
				PMI += npmi(aw, pw)
				count+=1
			elif ask_for == 'effect' and (pw+' '+aw) in Tuples:
				PMI += npmi(pw, aw)				
				count+=1
	if count:
		return PMI/count
	else:
		return 0

def npmi(w1, w2):
	global ask_for
        global maxlen
        global VocabP
	global VocabA
        global Tuples

	h = lambda x : -2*log(x,2)
	p_w1 = VocabP[pw] / maxlen
	p_w2 = VocabA[aw] / maxlen
	p_conj = Tuples[w1+' '+w2] / maxlen
		
	pmi = log(p_conj/(p_pw*p_aw), 10)
	npmi = pmi/h(p_conj)
	return npmi

def count_freq(D, key):
	if key in D: D[key]+=1
	else: D[key]=1
		

if __name__ == "__main__":
	n=0
	c=0
	P=[]
	A1=[]
	A2=[]
	VocabC={}
	VocabE={}
	Tuples={}
	with open('/home/irvin/python_practice_thesis/thesisBigData/tuples1705/cause-effect.txt','r', 'utf-8') as f: 
		for i,line in enumerate(f):
			entry = line.split(' ')
			count_freq(VocabC, entry[0])
			count_freq(VocabE, entry[1][:-1])
			count_freq(Tuples, line[:-1])
		
	maxlen=i	

	print "maxlen =", maxlen
	print pd.Series(VocabC)
	print pd.Series(VocabE)
	print pd.Series(Tuples)

	xfile = open("./copa/copa_conlled.txt", 'r', 'utf-8')
	tree = ET.parse('./copa/copa-dev.fr.xml')
	root = tree.getroot()
	for item in root.findall('item'):
		i = int(item.get('id'))
		ask_for = item.get('ask-for')
		answer = item.get('most-plausible-alternative') 

		if ask_for == 'cause':
			VocabP = VocabE
			VocabA = VocabC
		else:
			VocabP = VocabC
			VocabA = VocabE

		read_sentence(xfile, P)
		read_sentence(xfile, A1)
		read_sentence(xfile, A2)

		print
		print '('+str(i)+')'
		print ' '.join(P).encode('utf-8')
		print
		print ' '.join(A1).encode('utf-8')
		print
		print ' '.join(A2).encode('utf-8')
		print

		pmi1 = probability(P, A1)
		print 'pmi1 =', pmi1
		pmi2 = probability(P, A2)
		print 'pmi2 =', pmi2
		
		print '\n'
		if pmi1 > pmi2:
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
		
		P=[]
		A1=[]
		A2=[]
		n += 1
		break
		if i == 50:
			break

		
	xfile.close()
	print c/n

