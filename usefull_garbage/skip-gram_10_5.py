#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from gensim.models.keyedvectors import KeyedVectors
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
#import gensim, logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


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


def generate_valid_tuples(c_seq, e_seq):
	global maxlen
	batch = maxlen/100
	count = 0
	c_train = []
	e_train = []
	s = 0
	e = batch + s
	while 1:
		if e <= len(c_seq):#
			c_train = np.asarray(c_seq[s:e])
			e_train = np.asarray(e_seq[s:e])
			s = e+1#
			e = batch+s#
		else:
			e = len(c_seq)
			c_train = np.asarray(c_seq[s:e])
			e_train = np.asarray(e_seq[s:e])
			s = 0
			e = batch+s
		e_train = np_utils.to_categorical(e_train, eV+1)
		yield(c_train, e_train)


#		for c, e in zip(c_seq, e_seq):
#			if (c_frequent[c] and e_frequent[e]):
#				#print c, e
#				count += 1
#				c_train.append(c)
#				e_train.append(e)
#				if count % batch == 0:
#					c_train = np.asarray(c_train)
#					e_train = np.asarray(e_train)
#					e_train = np_utils.to_categorical(e_train, eV+1)
#					yield(c_train, e_train)
#					c_train = []
#					e_train = []

V=20000
maxlen = 10000
c_train = []
e_train = []
Causes=[]
Effects=[]
print "Reading input..."
with open('./tuples/cause-effect.txt','r') as f:
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
ew2i = eTokenizer.word_index
ei2w = {i:w for w,i in ew2i.items()}

print "  Causes..."
c_seq = cTokenizer.texts_to_sequences(Causes)
c_seq = [x[0] for x in c_seq]
#print c_seq
fdist = Counter(c_seq).most_common(V)
cv = [t[0] for t in fdist]
cV = len(cv)
#print cv
cv.sort()
for c in c_seq:
	c_frequent[c] = bin_search(cv, c) 
#print [ci2w[c] for c in cv]
#print c_frequent

print "  Effects..."
e_seq = eTokenizer.texts_to_sequences(Effects)
e_seq = [x[0] for x in e_seq]
#print e_seq
fdist = Counter(e_seq).most_common(V)
ev = [t[0] for t in fdist]
eV = len(ev)
print eV
ev.sort()
#print ev
for e in e_seq:
	e_frequent[e] = bin_search(ev, e)
#print e_frequent

print "Create skipgram..."

dim = 200
batch_size = 32
epochs = 10

skipgram = Sequential()
skipgram.add(Embedding(input_dim=cV+1, output_dim=dim, input_length=1, embeddings_initializer="glorot_uniform"))
skipgram.add(Reshape((dim, )))
skipgram.add(Dense(eV+1, activation='softmax'))

print skipgram.summary()

skipgram.compile(loss='categorical_crossentropy', optimizer="adadelta")

#print list(generate_valid_tuples(c_seq, e_seq, c_frequent, e_frequent))

print "Training..."		

c_seq_filt = []
e_seq_filt = []
for c, e in zip(c_seq_filt, e_seq_filt):
	if (c_frequent[c] and e_frequent[e]):
		c_seq_filt.append(c)
		e_seq_filt.append(e)

skipgram.fit_generator(generate_valid_tuples(c_seq_filt, e_seq_filt), steps_per_epoch=100, epochs=10)


#for ite in range(10):
#	loss = 0
#	for c_train, e_train in generate_valid_tuples(c_seq, e_seq, c_frequent, e_frequent):
#		#print c_train, e_train
#		e_train = np_utils.to_categorical(e_train, eV+1)
#		loss += skipgram.train_on_batch(c_train, e_train)
#	print(ite, loss)
	

f = open('vectors.txt' ,'w')
f.write(" ".join([str(cV),str(dim)]))
#f.write("\n")

vectors = skipgram.get_weights()[0]

for i, w in ci2w.items():
	f.write("\n")
	f.write(w)
	f.write(' ')
	f.write(' '.join(map(str, list(vectors[i,:]))))
	if i >= cV:
		break

f.close()

print "Predict..."

out = skipgram.predict(np.array([cw2i['guerre']])) 
print ei2w[np.argmax(out)+1]

#w2v = gensim.models.KeyedVectors.load_word2vec_format('./vectors.txt', binary=False)
#print w2v.most_similar(positive=['guerre'])
