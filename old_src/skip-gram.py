#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from codecs import open
import sys
from gensim.models.keyedvectors import KeyedVectors
from collections import Counter
from codecs import open
import numpy as np
from keras.preprocessing import sequence
from keras.utils import np_utils
import time
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Reshape
from keras.layers import Embedding
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.models import model_from_json
import h5py

import theano
theano.config.openmp = True

def write_fdist():
	global c_seq
	global e_seq
	global cV
	global eV
	global identity


	cfdist = Counter(c_seq).most_common(cV)
	with open('./predict/cause_fdist_'+identity+'.txt','w') as cf:
		for t in cfdist:
			i = t[0]
			f = str(t[1])
			cf.write(ci2w[i]+' '+str(i)+' '+f+'\n')

	efdist = Counter(e_seq).most_common(eV)
	with open('./predict/effect_fdist_'+identity+'.txt','w') as ef:
		for t in efdist:
			i = t[0]
			f = str(t[1])
			ef.write(ei2w[i]+' '+str(i)+' '+f+'\n')

def generate_valid_tuples(c_seaq_filt, e_seq_filt):
	global fit
	global maxlen
	global steps
	batch = maxlen/steps
	count = 0
	c_train = []
	e_train = []
	s = 0
	e = batch + s
	while 1:
		if e <= len(e_seq_filt):#
			c_train = np.asarray(c_seq_filt[s:e])
			e_train = np.asarray(e_seq_filt[s:e])
			s = e+1#
			e = batch+s#
		else:
			e = len(e_seq_filt)
			c_train = np.asarray(c_seq_filt[s:e])
			e_train = np.asarray(e_seq_filt[s:e])
			s = 0
			e = batch+s
		if fit == 'cat':
			e_train = np_utils.to_categorical(e_train, eV+1)
		yield(c_train, e_train)

print "Choose type of training:"
print "		cat (categorical-crossentropy and fit_generator)"
print "		sparse (sparse-categorical-crossentropy and fit_generator)"
print "		fit (sparse-categorical-crossentropy and fit)"
#fit = stdin.readline()
#if fit == '\n':
fit = 'fit'	#default

print "Choose number of tuples:"
maxlen = sys.argv[1]
if maxlen == '\n':
	maxlen = 1000000

maxlen = int(maxlen)
dim = 200
batch_size = 1000
epochs = 10
steps=1000
V=20000
Causes=[]
Effects=[]
Time = time.strftime("%H:%M:%S")
Date = time.strftime("%x")
identity = fit+'_'+Date[0:2]+'_'+Time+'_'+str(maxlen)
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
cV = min(V, len(cw2i))

print "  Effects..."
e_seq = eTokenizer.texts_to_sequences(Effects)
e_seq = [x[0] for x in e_seq]
eV = min(V, len(ew2i))


write_fdist()


print "Filter Vocabulary..."
c_seq_filt = []
e_seq_filt = []
for c, e in zip(c_seq, e_seq):
	if (c<=V and e<=V):
		c_seq_filt.append(c)
		e_seq_filt.append(e)

#print map(lambda i: (i, ci2w[i]), c_seq_filt[0:10])
#print map(lambda i: (i, ei2w[i]), e_seq_filt[0:10])


print "Create skipgram..."
cause_model = Sequential()
cause_model.add(Embedding(input_dim=cV+1, output_dim=dim, input_length=1, embeddings_initializer="glorot_uniform"))
cause_model.add(Reshape((dim, )))

effect_model = Sequential()
effect_model.add(Embedding(input_dim=eV+1, output_dim=dim, input_length=1, embeddings_initializer="glorot_uniform"))
effect_model.add(Reshape((dim, )))

skipgram = Sequential()
skipgram.add(Merge([word_model, context_model], mode="dot"))
skipgram.add(Dense(1, init="glorot_uniform", activation='softmax'))
skipgram.compile(loss="mean_squared_error", optimizer="adam")

print cause_model.summary()
print
print "Training..."		
if fit == 'cat':
	skipgram.compile(loss='categorical_crossentropy', optimizer="adadelta")
	skipgram.fit_generator(generate_valid_tuples(c_seq_filt, e_seq_filt), steps_per_epoch=steps, epochs=epochs)
else:
	skipgram.compile(loss='sparse_categorical_crossentropy', optimizer="adadelta")
	if fit == 'sparse':
		skipgram.fit_generator(generate_valid_tuples(c_seq_filt, e_seq_filt), steps_per_epoch=steps, epochs=epochs)
	elif fit == 'fit':
		c_seq_filt = np.asarray(c_seq_filt).astype(np.int16)
		e_seq_filt = np.asarray(e_seq_filt)
		skipgram.fit(c_seq_filt, e_seq_filt, batch_size=batch_size, epochs=epochs)


print "Saving vectors..."		
with open('./vectors/vectors_'+identity+'.txt' ,'w') as f:
	f.write(" ".join([str(cV),str(dim)]))
	vectors = skipgram.get_weights()[0]
	for i, w in ci2w.items():
		f.write("\n")
		f.write(w)
		f.write(' ')
		f.write(' '.join(map(str, list(vectors[i,:]))))
		if i >= cV:
			break

print "Saving model..."

# serialize model to JSON
model_json = skipgram.to_json()
with open("./models/model_"+identity+".json", "w") as json_file:
	json_file.write(model_json)
# serialize weights to HDF5
skipgram.save_weights("./models/model_"+identity+".h5")

print "Predict most similar words..."
print

out = skipgram.predict(np.array([cw2i['guerre']])) 
arr =  out.argsort()[0][-10:][::-1]
most_similar = [ei2w[i] for i in arr.tolist()]
print ' '.join(most_similar)

