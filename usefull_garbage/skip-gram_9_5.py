#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from collections import Counter
from nltk import FreqDist
from codecs import open
import numpy as np
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Reshape
from keras.layers import Embedding
from keras.layers import GlobalAveragePooling1D
from keras.datasets import imdb
import pandas as pd
from keras.preprocessing.text import Tokenizer


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


def generate_valid_tuples(c_seq, e_seq, c_frequent, e_frequent):
	for c, e in zip(c_seq, e_seq):
		if (c_frequent[c] and e_frequent[e]):
	
			yield(c, e)


V=4
maxlen = 10
c_train = []
e_train = []
Causes=[]
Effects=[]
print "Reading input..."
with open('/home/irvin/tuples27/cause-effect_0_2','r') as f:
	count = 0
	for line in f:
		tuple = line.split(' ')
		Causes.append(tuple[0])
		Effects.append(tuple[1][:-1])
		if count == maxlen :
			break
		count+=1

c_frequent = [True for x in range(0,len(Causes))]
e_frequent = [True for x in range(0,len(Causes))]

print "Preprocessing..."
cTokenizer = Tokenizer(filters = '')
cTokenizer.fit_on_texts(Causes)

eTokenizer = Tokenizer(filters='')
eTokenizer.fit_on_texts(Effects)

# construct mappings from words to indices and vice versa
cw2i = cTokenizer.word_index
ci2w = {i:w for w,i in cw2i.items()}
print ci2w

ew2i = eTokenizer.word_index
ei2w = {i:w for w,i in ew2i.items()}
print ei2w

print "Causes..."
c_seq = cTokenizer.texts_to_sequences(Causes)
c_seq = [x[0] for x in c_seq]
print c_seq
fdist = Counter(c_seq).most_common(V)
cv = [t[0] for t in fdist]
print cv
cv.sort()
print "frequent"
for c in c_seq:
	c_frequent[c] = bin_search(cv, c) 
#print [ci2w[c] for c in cv]
print c_frequent

print "Effects..."
e_seq = eTokenizer.texts_to_sequences(Effects)
e_seq = [x[0] for x in e_seq]
print e_seq
fdist = Counter(e_seq).most_common(V)
ev = [t[0] for t in fdist]
ev.sort()
print ev

for e in e_seq:
	e_frequent[e] = bin_search(ev, e)
print e_frequent

for c, e in generate_valid_tuples(c_seq, e_seq, c_frequent, e_frequent):
	print ci2w[c], ei2w[e]
	c_train.append(c)
	e_train.append(e)

c_train = np.asarray(c_train)
print len(c_train)
e_train = np.asarray(e_train)
e_train = np_utils.to_categorical(e_train, V+1)
#print e_train



dim = 200
batch_size = 32
epochs = 10

skipgram = Sequential()
skipgram.add(Embedding(embeddings_initializer="glorot_uniform", output_dim=dim, input_dim=V+1, input_length=1))
skipgram.add(Reshape((dim, )))
skipgram.add(Dense(V+1, activation='softmax'))

skipgram.compile(loss='categorical_crossentropy', optimizer="adadelta")
for ite in range(10):
	loss = 0
skipgram.fit(c_train, e_train, batch_size=batch_size, epochs=epochs)

