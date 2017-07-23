#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
import numpy as np
import sys
import nltk
from nltk.corpus import PlaintextCorpusReader
import re
import xml.etree.ElementTree as ET


def read_trigger(LU):
	name = LU.get('name')
	name = re.sub(ur"[']+","'_", name)
	name = re.sub(ur" ","_", name)
	return name.split('.')[0]


def find_children_of_triggers(L, children, triggerIDs, sentence, lineNum, file):	
	for i in range(0,lineNum):
		
		wordject = sentence.split('\n')[i]
		L.append([])
		L[i] = wordject.split('\t')
		#Quite tricky part
		parent_id = int(L[i][6])
		#we check for every word wether it is a child of a trigger or not.
		#wether it has one  of the triggers as parent. 
		if (parent_id in triggerIDs):
			#but, which of the triggers is it the parent of i?
			ID_index = triggerIDs.index(parent_id)
			children.append([])
			#2D-list: one column for each trigger-parent to store its children
			children[ID_index].append(i)
			file.write( "     TRIGGER's CHILDREN: " + L[i][1].encode('utf-8') + "\n")


def extract_triple(L, children, triggerIDs, file):
	for i in triggerIDs:
		childFound = False
		ID_index = triggerIDs.index(i)
		while children[ID_index]:
			child = int(children[ID_index].pop(0))	
			childFound = True
		if childFound:
			parent = int(L[i-1][6])-1 
			if L[parent][4] != 'PONCT' and L[i-1][1] != 'pour' and L[child][1]!= 'PONCT':
				triple = (L[parent][1], L[i-1][1], L[child][1]) 
				string = ''
				for s in triple:
					string = string + ' ' + s 
				file.write("----> " + string[1:].encode('utf-8') + '\n\n')


	
def isolate_pure_sentence(pureSentence, line):
	if line.split()[4] == 'PONCT':
		pureSentence = pureSentence[:-1] + line.split('\t')[1] + ' '
	else:
		pureSentence = pureSentence + line.split('\t')[1] + ' '

	return pureSentence
	

def extract(Dict, RE, File):
	line = unicode(sys.stdin.readline(), 'utf-8')
	word = ''
	sentence = ''
	pureSentence = ''
	count = 0
	sentNum = 0
	lineNum = 0
	children = {}
	triggerIDs = {}
	for key in Dict:
		triggerIDs[key] = []
		children[key] = []

	while line:	
		if len(line)>1:
			sentence = sentence + line
			lineNum += 1
			pureSentence = isolate_pure_sentence(pureSentence, line)

			#search for triggers
			for key in Dict:
				trigger = RE[key].search(line)				
				if trigger:
					word = trigger			#Let's store it somewhere. We will use it just as a boolean variable. 
					triggerIDs[key].append(lineNum)	#there might be more than one trigger in a sentence, we store them all
					children[key].append([])	#we will need this litte 2d-list to store all of the triggers' children
					pos.append(key)
					break
					
		else:
			#A whole sentence is extracted 
			L = {}
			if word:
				#Yep, somewhere in this sentence there is a trigger. 
				count += 1
				sentNum += 1	
				for key in pos:
					L[key] = []
					File[key].write(str(sentNum)+') '+pureSentence.encode('utf-8')+'\n'+sentence.encode('utf-8')+'\n')
					find_children_of_triggers(L[key], children[key], triggerIDs[key], sentence, lineNum, File[key])
					extract_triple(L[key], children[key], triggerIDs[key], File[key])

			pos = []
			lineNum = 0
			word = ''
			sentence = ''
			pureSentence = ''
			children = {}
			triggerIDs = {} 
			for key in Dict:
				triggerIDs[key] = []
				children[key] = []
		line = unicode(sys.stdin.readline(), 'utf-8')



if __name__ == "__main__":

	tree = ET.parse('/Asfalda/framenet/fndata-asfalda/frame/Causation.xml')
	root = tree.getroot()
	xmlns = "{http://framenet.icsi.berkeley.edu}"
	Dict = {'adv': '', 'a': '', 'c': '', 'n': '', 'v': '', 'conj': '', 'prep': ''}
	RE = {}
	File = {}

	for LU in root.findall(xmlns + 'lexUnit'):
		pos = LU.get('POS')
		name = read_trigger(LU)
		if name != "pour":
			Dict[pos] = Dict[pos] + name + "	|"		

	for key in Dict:
		Dict[key] = ur"" + Dict[key][:-1]
		print Dict[key].encode('utf-8') + '\n'
		RE[key] = re.compile(Dict[key], re.M|re.I|re.U|re.L) 
		File[key] = open("./text/text_" + key + ".txt", "w")

	extract(Dict, RE, File)			

	for key in Dict:
		File[key].close()
