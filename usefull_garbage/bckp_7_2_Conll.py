#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# command to run the programme: $python Conll.py < /path/to/connlFile

import os
import numpy as np
import sys
import nltk
from nltk.corpus import PlaintextCorpusReader
import re
import xml.etree.ElementTree as ET

tree = ET.parse('/Asfalda/framenet/fndata-asfalda/frame/Causation.xml')
root = tree.getroot()
reCausationPrep = ""


def read_trigger():
	name = LU.get('name')
	name = re.sub(ur"[']+","'_", name)
	name = re.sub(ur" ","_", name)
	return name.split('.')[0]


xmlns = "{http://framenet.icsi.berkeley.edu}"
trig = ''
Prep=[]
for LU in root.findall(xmlns + 'lexUnit'):
	pos = LU.get('POS')
	name = read_trigger()
	#print name.encode('utf-8')
	if pos == 'prep' and name != 'pour':
		reCausationPrep = reCausationPrep + name +"	|" 
	elif pos ==
def extract(re):
reCausationPrep = ur"" + reCausationPrep[:-1]	
#print reCausationPrep.encode('utf-8')
stream = sys.stdin
lineASCII = stream.readline()
line = unicode(lineASCII, 'utf-8')

sentence = ''
pureSentence = ''
word = ''
sentNum = 0
lineNum = 0
IDs = []
words = []
children = []

string = ur"au_point_de|d'_où|du_fait_de|en_raison_de|faute_de|grâce_à|jusqu'_à|par_la_faute_de|pour_cause_de|sous_l'_effet_de|à_cause_de|à_défaut_de|à_force_de|à_l'_origine_de|à_la_suite_de"#pour
count = 0
RE = re.compile(reCausationPrep, re.M|re.I|re.U|re.L)	#variable RE contains a regular expression

while line:	
	if len(line)>1:
		flag = True		#flag is used in a condition below to 
					#avoid counting empty lines as new sentences
		trigger = RE.search(line)				#let's search for triggers
		lineNum += 1

		#isolate pure sentence
		pos = line.split()[4]
		if pos == 'PONCT':
                	pureSentence = pureSentence[:-1] + line.split('\t')[1] + ' '
                else:
			pureSentence = pureSentence + line.split('\t')[1] + ' '


		if trigger:
			#Guess what! We found a trigger!
			word = trigger			#Let's store it somewhere. We will use it just as a boolean variable. 
			IDs.append(lineNum) 		#Warning: there might be more than one triggers in one sentence 
							#we store the ids of every and each of them
			words.append(trigger.group())	#we do the same with their names. It might be useful/
			children.append([])		#we will need this litte 2d-list to store all of triggers' children
		sentence = sentence + line
	else:
		#This is where a whole sentence is extracted and it's ready for further parsing
		L = []

		if word and flag:
		#Yep, somewhere in this sentence there is a trigger. 
		#Let's store every word(ob)ject of the current sentence in a list L.

			sentNum += 1	
			print str(sentNum)+ ') '  + pureSentence.encode('utf-8')
			flag = False
		#	print(IDs)
			for i in range(0,lineNum):
				wordject = sentence.split('\n')[i]
				L.append([])
				L[i] = wordject.split('\t')
				#for each and every trigger found in the sentence we will find its child(ren)
				parent_id = int(L[i][6])
				if (parent_id in IDs):
					ID_index = IDs.index(parent_id)
					children.append([])
					children[ID_index].append(i)
					print "     TRIGGER's CHILDREN: " + L[i][1].encode('utf-8')
			count += 1
			#Now, let's just extract the holy grail for each and every trigger found in the current sentence.
			for i in IDs:
				childFound = False
				ID_index = IDs.index(i)
				
				while children[ID_index]:
#TODO: now in var child we store only the id of one of the triggers children. Maybe we need to keep all of them or a specific one...
#TODO: print children and the whole sentence to check everything
					child = int(children[ID_index].pop(0))	
					childFound = True
					#print(i)
				if childFound:
					parent = int(L[i-1][6])-1 
					if L[parent][4] != 'PONCT':
						triple = (L[parent][1], L[i-1][1], L[child][1]) 
						string = ''
						for s in triple:
							string = s + ' ' + string
						print string.encode('utf-8') + '\n'
		children = []
		IDs = []
		lineNum = 0
		word = ''
		sentence = ''
		pureSentence = ''

			
	lineASCII = stream.readline()
	line = unicode(lineASCII, 'utf-8')


