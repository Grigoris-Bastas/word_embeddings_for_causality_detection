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
causeStr = sys.argv[1]
effectStr = sys.argv[2]
identity = sys.argv[3]	
maxlen = 1000000
V=20000


cw2i = {}
ci2f = {}
cw2f = {}
ew2i = {}
ei2f = {}
with open('./predict/cause_fdist_'+identity+'.txt','r') as cf:
	for line in cf:
		entry = line.split(' ')
		w = entry[0]
		i = int(entry[1])
		f = int(entry[2])
		cw2i[w] = i
		ci2f[i] = f
		cw2f[w] = f


with open('./predict/effect_fdist_'+identity+'.txt','r') as ef:
	for line in ef:
		entry = line.split(' ')
		w = entry[0]
		i = int(entry[1])
		f = int(entry[2])
		ew2i[w] = i
		ei2f[i] = f

ei2w = {i:w for w,i in ew2i.items()}

print "Loading file.."
# load json and create model
json_file = open('./models/model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
skipgram = model_from_json(loaded_model_json)
# load weights into new model
skipgram.load_weights("./models/model.h5")

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


out = skipgram.predict(np.array([cw2i[causeStr]]))
#print ' '.join(str(out[0][0:20].tolist()))
#out = [log(prob*(maxlen/(cw2f[causeStr]*ci2f[index])),10) for index,prob in enumerate(out[0]) if index!=0]	#idf

print ' '.join(str(out[0][0:30]))
out = [npmi(prob, index, causeStr) for index,prob in enumerate(out[0])]	#idf #SOS!! forgot 0
print
print ' '.join(str(out[0:30]))

out = np.array(out)
arr =  out.argsort().tolist()
#arr =  out.argsort()[-20:][::-1].tolist()
print ' '.join(str(arr))
print arr.index(ew2i[effectStr])
#print arr
most_likely = [ei2w[i] for i in arr if i!=0]

print ' '.join(most_likely[0:15])


