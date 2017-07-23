#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# command to run the programme: $python Conll.py < /path/to/connlFile


import numpy as np
import sys
import nltk
from nltk.corpus import PlaintextCorpusReader
import re

stream = sys.stdin
lineASCII = stream.readline()
line = unicode(lineASCII, 'utf-8')

sentence = ''
word = ''
sentNum = 0
lineNum = 0
trigger = ''
trigNum = 0
indexes = []
words = []

while line:	
	if len(line)>1:
		flag = True		#flag is used in a condition below to 
					#avoid counting empty lines as new sentences
	
		RE = re.compile(ur'à_cause_de', re.M|re.I|re.U|re.L)	#variable RE contains a regular expression
		trigger = RE.search(line)				#let's search for triggers
		lineNum += 1
		if trigger:
			#Guess what! We found a trigger!
			word = trigger			#Let's store it somewhere. We will use it just as a boolean variable. 
			trigNum +=1
			indexes.append(lineNum) 	#Warning: there might be more than one triggers in one sentence 
							#we store the ids of every and each of them
			words.append(trigger.group())	#we do the same with their names. It might be useful/
				

		sentence = sentence + line
	else:
		L = []
		children = []
		if word and flag:
		#Yep, somewhere in this sentence there is a trigger. Let's play with this sentence.
		#Let's store every word and its tags in a list L.

		#	print(sentence)
			sentNum += 1	
			flag = False
			for i in range(0,lineNum):
				lineTags = []
				wordject = sentence.split('\n')[i][:]
		#		print wordject
				L.append([])
				for j in range(0,9):
					tag = (wordject.split('\t')[j])
					lineTags.append(tag)
					L[i].append(tag)
				if (int(lineTags[6]) in indexes):
					children.append(i)

		#	print(indexes)
		#	print(L)

			#Now, let's just extract the holy grail for each and every trigger found in the current sentence.
			for i in indexes:
				child = int(children.pop(0))
		#		print(i)
				triple = (L[ int(L[i-1][6])-1 ][1], L[i-1][1], L[child][1]) 
				print triple

		#	break		
		indexes = []
		lineNum = 0
		trigNum = 0
		word = ''
		sentence = ''

			
	lineASCII = stream.readline()
	line = unicode(lineASCII, 'utf-8')


