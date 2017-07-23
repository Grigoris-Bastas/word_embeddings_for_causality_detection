#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import enchant
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
from nltk.corpus import stopwords
from nltk.stem.snowball import FrenchStemmer

#e.g. python createTrainingTuples.py ~/python_practice_thesis/thesisBigData/xml_extractions/extractions_0382.xml

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


count = 0

stemmer = FrenchStemmer()

nltk_stopwords = stopwords.words('french')
nltk_stopwords.sort()

Stopwords = [u"être","avoir","faire","aller","venir","devoir","rendre","falloir","pas","ne","l","l'","trop","plus",
             u"ne_être","ne_avoir","ne_faire","ne_aller","ne_venir","ne_devoir","ne_rendre","ne_falloir", 'pouvoir', 'ne_pouvoir', 'devenir' 
             u"très","tout",u"même","non","cln"] 
Stopwords.sort()

StopPos = ['CS','CC',  'CLO', 'CLR', 'P', 'P+D', 'PRO', 'ADJWH', 'PROREL', 'ADV', 'NPP', 'ET', 'DET']
StopPos.sort()

fr = enchant.Dict('fr_FR')
with open(sys.argv[1], 'r') as xml_file:
	xml_tree = etree.parse(xml_file)
	root = xml_tree.getroot()
	for Tuple in root:
		frame = Tuple.get('frame')
		trPos = Tuple.get('pos')
		C = []
		E = []
		for Event in Tuple:
			event = Event.tag
			type = Event.get('type')
			for Category in Event:
				category = Category.tag
				numOfWords = Category.get('numOfWords')
				phrase = Category.get('phrase')
				for Word in Category:
					#wi = int(Word.tag[1])
					word = Word.get('word')
					pos = Word.get('pos')
					dist = int(Word.get('dist'))
					lemma = Word.get('lemma')
					#stem = Word.get('stem')
					#synt = Word.get('synt')
					#if pos=='NPP':
					#	if synt=='suj':
					#		lemma='NPP'
					#	elif synt=='obj':
					#		lemma='NPP'

					if lemma[:2] in ["l'","d'"]:
						lemma = lemma[2:]

					if (
						dist > 12 or
				#		frame[0:10] != 'Causation/' or
						(not lemma[0].isalpha()) or
						lemma[0].isupper() or
						len(lemma) == 1 or
						lemma[-1] == '.' or
						(not fr.check(lemma)) or
						bin_search(StopPos, pos) or
						bin_search(Stopwords, lemma) or
						bin_search(nltk_stopwords, lemma)

					   ):
						continue
					#print lemma, pos, lemma, bin_search(StopPos, pos) 	

					# not used yet
					EventCause = (event == 'cause')
					FramePurpose = (frame == 'FR_Means_for_purpose/')	#don't use Purpose frames
					FrameCausation = (frame[0:10] == 'Causation/')		#use only Causation frames

					if EventCause:
						C.append('cs_'+lemma)
					else:
						E.append('ef_'+lemma)

		dir = '/home/irvin/python_practice_thesis/thesisBigData/tuples1106_allFR_dist12_csef/' 
		causeFile = dir+'cs_cause-ef_effect.txt'
		with open(causeFile, 'a','utf-8') as cf:
			for cause in C:
				for effect in E:
					cf.write(cause + ' ' + effect+'\n')

