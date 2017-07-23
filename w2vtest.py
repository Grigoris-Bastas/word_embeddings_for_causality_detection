#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from codecs import open
import operator
from math import log
import os
import gensim
import sys
import numpy as np
import pandas as pd
from numpy import linalg as LA
from gensim.models.keyedvectors import KeyedVectors
from nltk.stem.snowball import FrenchStemmer

def npmi(w1, w2):
        global maxlen
        global VocabC
        global VocabE
        global Tuples

	w1 = w1.decode('utf-8')
	w2 = w2.decode('utf-8')
	pair = w1+' '+w2

	if pair in Tuples:
		h = lambda x : -2*log(x,2)
		p_w1 = VocabC[w1] / maxlen
		p_w2 = VocabE[w2] / maxlen
		p_conj = Tuples[pair] / maxlen

		pmi = log(p_conj/(p_w1*p_w2), 10)
		npmi = pmi / h(p_conj)
		return npmi
	else:
		return -1

def count_freq(D, key):
        if key in D: D[key]+=1
        else: D[key]=1


if __name__ == "__main__":

	fname = '/home/irvin/python_practice_thesis/thesisBigData/'
	ftuple = 'tuples2405_allFR_dist8_csef/cs_cause-ef_effect.txt'

        VocabC={}
        VocabE={}
        Tuples={}

	vecfile = sys.argv[1] 
	#string = sys.argv[2]
	#context =  sys.argv[3]
	#print string, context

	with open(fname+ftuple, 'r', 'utf-8') as f:
		for i, line in enumerate(f):
			entry = line.split(' ')
			count_freq(VocabC, entry[0])
			count_freq(VocabE, entry[1][:-1])
			count_freq(Tuples, line[:-1])
			#T.append(line)
			#if i==10000:
			#       break
	maxlen = i
	print "Read!"

        print "maxlen =", maxlen
        print pd.Series(VocabC)
        print pd.Series(VocabE)
        print pd.Series(Tuples)


	model = gensim.models.Word2Vec.load(fname+vecfile)
	
	while True:
		string = raw_input('Give me the cause: ')
		context = raw_input('Give the effect: ')

		string = 'cs_'+string
		context = 'ef_'+context

		try:
			s = model.wv.index2word.index(string)
			c = model.wv.index2word.index(context)
			print
			print 'vector_cos = ', np.inner(model.syn1neg[s], model.wv.syn0[c]) #TODO: try simply syn1
			print 'pmi = ', npmi(string, context)
			print

		except ValueError:
			continue

#TODO: calculate top ten using stanford's method
#print model.wv.syn0
#print model.wv.syn0[model.wv.index2word.index(string)] == model[string]

#print model.wv.index2word.index('cs_guerre')
#print np.inner(model[string], model[context])

#model2 = gensim.models.Word2Vec.load(fname2)
#####print '1) '+' '.join([t[0][0:] for t in model.wv.most_similar(positive=[string])])
#print '2) '+' '.join([t[0][0:] for t in model2.wv.most_similar(positive=[string])])

#path = 'word2vecf_extractions/cause_vectors.txt'
#w2v = gensim.models.KeyedVectors.load_word2vec_format(path, binary=False)
#print 'f) '+' '.join([t[0] for t in w2v.most_similar(positive=[string])])

#cpath = 'word2vecf_extractions/cause_vectors.txt'
#epath = 'word2vecf_extractions/effect_vectors.txt'
#
#
#cw2v = gensim.models.KeyedVectors.load_word2vec_format(cpath, binary=False)
#vector = cw2v[string]
#print LA.norm(vector)
#
#ew2v = gensim.models.KeyedVectors.load_word2vec_format(epath, binary=False)
#
#print ' '.join([t[0] for t in ew2v.most_similar(positive=[vector])])
#print ' '.join([t[0] for t in w2v.doesnt_match(string)])

