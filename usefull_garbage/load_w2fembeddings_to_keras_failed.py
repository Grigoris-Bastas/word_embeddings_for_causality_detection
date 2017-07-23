#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from __future__ import division
import sys
import h5py
from math import log
from keras.preprocessing.text import Tokenizer
from gensim.models.keyedvectors import KeyedVectors
from collections import Counter
import numpy as np
from keras.models import model_from_json
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Reshape
from keras.layers import Embedding

def npmi(prob, index, string):
	global maxlen
	global cw2f
	global ci2f
	pmi = log(prob / ei2f[index], 10)
	h = lambda x : -2*log(x,2)
	pconj = h(prob*cw2f[string])
	npmi = pmi / pconj
	return npmi

causeStr = sys.argv[1]
effectStr = sys.argv[2]
identity = sys.argv[3]	

maxlen = 1000000
V=20000

c2i = {}
ci2f = {}
cw2f = {}
ew2i = {}
ei2f = {}



i = 1
with open('./word2vecf_extractions/causeVecf.txt','r') as f:
	line = f.readline()
	voc = int(line.split(' ')[0]) + 1
	embedding_weights = np.zeros((voc, 200))
	for line in f:
		entry = line.split(' ')
		w = entry[0]
		c2i[w] = i
		vector = np.asarray(map(np.float32,entry[1:-1]))
		embedding_weights[i,:] = vector
		i+=1


skipgram = Sequential()
skipgram.add(Embedding(voc, 200, input_length=1, weights=[embedding_weights], trainable=False))
skipgram.add(Reshape((200,)))
skipgram.add(Dense(voc, activation='softmax'))

out = skipgram.predict(np.array([c2i[causeStr]]))


#out = [npmi(prob, index, causeStr) for index,prob in enumerate(out[0]) if index!=0]	#idf
#print ' '.join(str(out))
out = np.asarray(out)
arr =  out.argsort().tolist()
print arr[0]
#arr =  out.argsort()[-20:][::-1].tolist()
print ' '.join(str(arr[0][0:20]))
print arr[0].index(107)
#print arr
#most_likely = [ei2w[i] for i in arr if i!=0]

#print ' '.join(most_likely[0:30])


