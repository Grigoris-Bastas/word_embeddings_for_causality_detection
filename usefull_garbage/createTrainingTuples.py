#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from codecs import open
from itertools import chain, combinations
from copy import deepcopy
import os
import numpy as np
import sys
import re
import io
import xml.etree.ElementTree as etree
from itertools import islice

#TODO: two different training sets, one for cause-effect and one for effect-cause tuples

def write(causeFile, effectFile, C, E):
	with open(causeFile,'a','utf-8') as cf:
		for cause in C:
			for effect in E:
				if (cause == effect == 'cln') or (cause == effect  == 'NPP'):
					continue
				cf.write(cause + ' ' + effect+'\n')
	with open(effectFile,'a', 'utf-8') as ef:
		for cause in C:
			for effect in E:
				if (cause == effect == 'cln') or (cause == effect  == 'NPP'):
					continue
				ef.write(effect + ' ' + cause+'\n')

Stopwords = [u"être","avoir","faire","aller","venir","devoir","rendre","falloir","pas","ne","l","l'","trop","plus","beaucoup","aussi","encore",
             u"ne_être","ne_avoir","ne_faire","ne_aller","ne_venir","ne_devoir","ne_rendre","ne_falloir", 
             u"très","que","tout",u"même","non","ainsi","juste"] 


StopPos = ['CS','CC',  'CLO', 'CLR', 'P', 'P+D', 'PRO', 'ADJWH', 'PROREL']

LENGTH = 4

with open(sys.argv[1], 'r') as xml_file:
	xml_tree = etree.parse(xml_file)
	root = xml_tree.getroot()
	for Tuple in root:
		flag = True
		frame = Tuple.get('frame')
		trPos = Tuple.get('pos')
		MaxC = MaxE = 0
		C = [[[] for j in range(0,50)] for i in range(0,LENGTH)]
		E = [[[] for j in range(0,50)] for i in range(0,LENGTH)]
		for Event in Tuple:
			event = Event.tag
			type = Event.get('type')
			for Category in Event:
				category = Category.tag
				numOfWords = Category.get('numOfWords')
				phrase = Category.get('phrase')
				for Word in Category:
					wi = int(Word.tag[1])
					word = Word.get('word')
					pos = Word.get('pos')
					dist = int(Word.get('dist'))
					lemma = Word.get('lemma')
					stem = Word.get('stem')
					synt = Word.get('synt')

					if (
						len(lemma) == 1 or
						lemma in Stopwords or
						pos in StopPos or
						word[0].isdigit() or
						pos == 'ADV' or
						dist > 5
					   ):
						flag = False
						continue

					if pos=='NPP':
						if synt=='suj':
							lemma='NPP'
						elif synt=='obj':
							lemma='NPP'
							
					if lemma[:2] in ["l'","d'"]:
						lemma = lemma[2:]

					# not used yet
					EventCause = (event == 'cause')
					FramePurpose = (frame == 'FR_Means_for_purpose/')	#don't use Purpose frames
					FrameCausation = (frame[0:10] == 'Causation/')		#use only Causation frames

					Conditions = [FrameCausation]
					PowerSet = chain.from_iterable(combinations(Conditions,r) for r in range(len(Conditions)+1))
					for i,condition in enumerate(PowerSet):
						conjunction = True
						for p in condition:
							conjunction = conjunction and p
						if conjunction:
							if EventCause:
								C[i][dist].append(lemma)
							else:
								E[i][dist].append(lemma)

		dir = './tuples/' 
		for i in range(0, LENGTH):					
			if C[i][0] and E[i][0]: 	#not empty	
				for d in range(1,5):
					C[i][d] = C[i][d] + C[i][d-1]
					E[i][d] = E[i][d] + E[i][d-1]

				for d in [2]: #range(0,5):
					causeFile = dir+'cause-effect_'+str(i)+'_'+str(d)
					effectFile = dir+'effect-cause_'+str(i)+'_'+str(d)
					write(causeFile, effectFile, C[i][d], E[i][d])


