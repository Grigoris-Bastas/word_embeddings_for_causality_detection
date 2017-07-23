#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
import numpy as np
import sys
import nltk
from nltk.corpus import PlaintextCorpusReader
import re
import xml.etree.ElementTree as ET

#def find_verb_expression(A,L):
#	#TODO: find children of A and check when-if you should find the children of children
#	#ChildA = find_children()
#	if A[3] == 'V' and child### == 'N':
#		AA = [A, child###]
#	else:
#		AA = [A]
#	#initialize Mix
#	Mix = []
#	for i in A:
#		Mix.append('')
#		
#	for i in range(len(AA)):
#		for j in range(len(AA[i])):
#			Mix[j] = Mix[j] + '-' + AA[i][j]
#	for j in range(len(Mix)):
#		Mix[j] = Mix[j][1:]
#	return Mix

def read_trigger(LU):
	name = LU.get('name')
	name = re.sub(ur"[']+","'_", name)
	name = re.sub(ur" ","_", name)
	return name.split('.')[0]


def find_children(L, children, triggerIDs, lineNum):	
	for i in range(0,lineNum):
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


def extract_triple(L, children, triggerIDs, df):
	for i in triggerIDs:
		ID_index = triggerIDs.index(i)
		while children[ID_index]:
			child = int(children[ID_index].pop(0))	
			parent = int(L[i-1][6])-1 
			A = L[parent]
			B = L[i-1]
			C = L[child]
			#if A[4]!='PONCT' and  A[4]!='CC' and C[4]!='PONCT' and C[4]!='CC':
				#MA = find_verb_expression(A,L)

			triple = (A[2], B[2], C[2]) 
			POS = (A[4], B[4], C[4])
			Synt = (A[7], B[7], C[7])
			s= []
			for (mot,pos,synt) in zip(triple,POS,Synt):
				s.append(mot.encode('utf-8') + '{' + pos.encode('utf-8') + '|' + synt.encode('utf-8') + '}')
			for j in {0,1}:
				if (A[3]=='V' or A[3]=='N' or A[3]=='ADJ') and C[4]=='NC': 
					df[j].write("------->  ")
				elif A[4]=='PONCT' or  A[4]=='CC' or C[4]=='PONCT' or C[4]=='CC':
					df[j].write("$$$$$$$>  ")
				else:
					df[j].write("xxxxxxx>  ")

				df[j].write("{0:35}{1:35}{2:25}".format(s[0], s[1], s[2]))
				df[j].write('\n\n\n')

	
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
	count = {'adv': 0, 'a': 0, 'c': 0, 'n': 0, 'v': 0, 'conj': 0, 'prep': 0}
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
				sentNum += 1	
				#We use this "key" thing because we might detect multiple triggers of different types in the same sentence
				for key in pos:
					count[key] += 1
					L[key] = []
					adj[key] = []
					#list of sentence's wordjects(=word&tags)
					L[key].append
					for i in range(0,lineNum):
						L[key].append([])
						AdjL[key].append([])
						wordject = sentence.split('\n')[i]
						L[key][i] = wordject.split('\t')

def create_adjacencey_list(AdjList, Sentence) 
	for i in range(0,len(Sentence))
		parent = int(L[i+1][6])
		AdjList[parent].append(i+1)		

	return AdjList
					AdjL[key] = create_adjacency_list(adjL[key], L[key], )[:]

					find_children(L[key], children[key], triggerIDs[key], sentence, lineNum, File[key])
					#write sentence in file
					if children[key][0]:
						File[key][0].write(str(count[key])+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n'+								    sentence.encode('utf-8')+'\n')
						File[key][1].write(str(count[key])+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n\n')
					#write triple in file
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
	File = {'adv': [], 'a': [], 'c': [], 'n': [], 'v': [], 'conj': [], 'prep': []}


	for LU in root.findall(xmlns + 'lexUnit'):
		pos = LU.get('POS')
		name = read_trigger(LU)
		if name != "pour" and name!="comme":
			Dict[pos] = Dict[pos] + name + "	|"		

	for key in Dict:
		Dict[key] = ur"" + Dict[key][:-1]
		print key + ': ' + Dict[key].encode('utf-8') + '\n'
		RE[key] = re.compile(Dict[key], re.M|re.I|re.U|re.L) 
		File[key].append(open("./text/text_" + key + ".txt", "w"))
		File[key].append(open("./text/text_" + key + "_pure_triple.txt", "w"))

	extract(Dict, RE, File)			

	for key in Dict:
		for i in {0,1}:
			File[key][i].close()
