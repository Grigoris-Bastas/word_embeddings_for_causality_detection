#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import nltk
from nltk.corpus import PlaintextCorpusReader

corpus_root = '/home/irvin/Dropbox/Thesis'

corpusList = PlaintextCorpusReader(corpus_root,['xaa','frwac_1134.parsed.marked'])

Conll = corpusList.words('frwac_1134.parsed.marked')

aCauseDe = Conll.count(u'à_cause_de')

print aCauseDe

#ParceQue = Conll.count('parce_que')

#conl.index(u'à_cause_de')

#print(conl[113759])

#with open('/home/irvin/Dropbox/Thesis/frwac_1134.parsed.marked') as fd:
#	string = fd.read()
#
#with open('/home/irvin/Dropbox/Thesis/frwac_1134.parsed.marked') as fd:
#	num_of_lines = len(fd.readlines()) 
#
#print(num_of_lines)
#words = string.split('\t' or '\n')[1]
#for i in range(10,(num_of_lines-10)*9,9):
#	words = words + ' ' + string.split('\t' or '\n')[i]
#
##word = string.split('\t' or '\n')[19]
#
#print(words)
