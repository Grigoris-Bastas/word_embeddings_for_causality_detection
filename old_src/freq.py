import os
import sys
from codecs import open
import nltk


V = []
f = open(sys.argv[1],'r', 'utf-8')              # ususally sys.argv[1] = wv or cv
for line in f:
        word = line.split(' ')[0]
	L[word] = 0
        V.append(word)

path = '/home/irvin/python_practice_thesis/corpus/'
Vocabulary = []
LU = []
Times = {}
superSum = 0
for frwacVoc in os.listdir(path):
       frw = open(path+frwacVoc, 'r', 'utf-8')
       print frwacVoc
       sum = frw.readline()
       superSum += int(sum)
       next (frw)
       for lineFrwac in frw:
	       entryFrwac = lineFrwac.split()
	       LU.append(entryFrwac[1])
	       Times[entryFrwac[1]] = int(entryFrwac[0])
       print Times['vitesse']

       for word in T:
	       if bin_search(LU, u'vitesse'):
		       print word
		       T[word] += Times[word]


