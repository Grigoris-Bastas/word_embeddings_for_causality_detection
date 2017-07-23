#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from copy import deepcopy
import os
import numpy as np
import sys
import nltk
from nltk.corpus import PlaintextCorpusReader
import re
import xml.etree.ElementTree as ET


def capture_verb_phrase(A,v,AdjL,L,trigID):
	child = -1
	if v > 0:	#check validity o vertex
		while AdjL[v]:
			
			child = AdjL[v].pop()
			if child!=trigID and (L[child-1][4] in ['NC','ADV','ADJ','VPP','VINF']):
				if L[child-1][7] == 'obj':
					for j in {2,4,7}:	
						A[j] = A[j] + '~' + L[child-1][j]
					break

				elif L[child-1][7] == 'suj':	
					for j in [2,4,7]:
						A[j] = L[child-1][j] + '~' + A[j]
					break

				elif (L[child-1][7] in ['mod', 'ats']) and (child <= v+10 and child >= v-10):
					for j in {2,4,7}:	
						A[j] = A[j] + '~' + L[child-1][j]
					break
	return child	
		
				
					
def read_trigger(LU):
	name = LU.get('name')
	name = re.sub(ur"[']+","'_", name)
	name = re.sub(ur" ","_", name)
	return name.split('.')[0]


def extract_triple(L, AdjL, triggerIDs, df):
	flag = True
	for trigID in triggerIDs:
		if L[trigID-1][7] != 'root':
			parent = int(L[trigID-1][6]) 
			for child in AdjL[trigID]:
				AdjList = deepcopy(AdjL)	#deepcopy saved me (it generates list with new id, so pop() has no effect)
				A = L[parent-1][:]
				B = L[trigID-1]
				C = L[child-1]
				#if A[3]== 'V':
				sonOfParent = capture_verb_phrase(A,parent,AdjList,L,trigID)
		
				SonOfChild = capture_verb_phrase(C,child,AdjList,L,trigID)

				grandsonOfParent = capture_verb_phrase(A,sonOfParent,AdjList,L,trigID)

				df[0].write("Parents' sons: " + str(AdjL[parent]) + "	Children's sons: " + str(AdjL[child]))	
				df[0].write('\n\n')
				for i in {0,1,2}:
					if (A[3] in ['V','N','A']) and (C[3] in ['V','N']): 
						df[i].write("------->  ")
					elif (A[4] in ['PONCT','CC','PONCT']) or C[4]=='CC':
						df[i].write("$$$$$$$>  ")
					else:
						df[i].write("xxxxxxx>  ")

					df[i].write((A[2]+'{'+A[4]+'|'+A[7]+'}\t\t').encode('utf-8'))
					df[i].write((B[2]+'{'+B[4]+'|'+B[7]+'}\t\t').encode('utf-8'))
					df[i].write((C[2]+'{'+C[4]+'|'+C[7]+'}\t\t').encode('utf-8'))
					df[i].write('\n\n\n')


def preliminary_write(df,count,triggerIDs,AdjL,sentNum,sentence,pureSentence):
	flag = True
	for trigID in triggerIDs:
		if AdjL[trigID] and flag:
			#write sentence in file
			df[0].write(str(count)+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n'+sentence.encode('utf-8')+'\n')
			df[1].write(str(count)+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n\n')
			df[2].write(str(count)+'|'+str(sentNum)+') ')
			flag = False
	
def isolate_pure_sentence(pureSentence, line):
	if line.split()[4] == 'PONCT':
		pureSentence = pureSentence[:-1] + line.split('\t')[1] + ' '
	else:
		pureSentence = pureSentence + line.split('\t')[1] + ' '

	return pureSentence
	
def create_adjacency_list(AdjList, Parent):
	for i in range(0, len(Parent)+1):
		AdjList.append([])
	for i in range(0, len(Parent)):
		parent = int(Parent[i][6])
		AdjList[parent].append(i+1)		

	return AdjList


def extract(Dict, RE, File):
	line = unicode(sys.stdin.readline(), 'utf-8')
	count = {'a': 0, 'c': 0, 'n': 0, 'v': 0, 'conj': 0, 'prep': 0}
	triggerIDs = {'a': [], 'c': [], 'n': [], 'v': [], 'conj': [], 'prep': []}
	word = ''
	sentence = ''
	pureSentence = ''
	sentNum = 0
	lineNum = 0

	while line:	
		if len(line)>1:
			sentence = sentence + line
			lineNum += 1
			pureSentence = isolate_pure_sentence(pureSentence, line)

			#search for triggers
			#We use this "key" thing because we might detect multiple triggers of different types in the same sentence
			for key in Dict:
				trigger = RE[key].search(line)				
				if trigger:
					if line.split('\t')[3][0] == key[0].upper(): #check the part-of-speech
						word = trigger			#Let's store it somewhere. 
						triggerIDs[key].append(lineNum)	#there might be more than one trigger in a sentence
						if key not in pos:
							pos.append(key)
					
		else:
			#A whole sentence is extracted 
			if word:
				#Yep, somewhere in this sentence there is a trigger. 
				L = []
				AdjL = []
				sentNum += 1	

				#list of sentence's wordjects(=word&tags)
				for i in range(0,lineNum):
					wordject = sentence.split('\n')[i]
					L.append(wordject.split('\t'))

				AdjL = create_adjacency_list(AdjL, L)

				for key in pos:
					count[key] += 1
					preliminary_write(File[key], count[key], triggerIDs[key], AdjL, sentNum, sentence, pureSentence)
					#write triple in file
					extract_triple(L, AdjL, triggerIDs[key], File[key])
					

			pos = []
			lineNum = 0
			word = ''
			sentence = ''
			pureSentence = ''
			triggerIDs = {} 
			for key in Dict:
				triggerIDs[key] = []
		line = unicode(sys.stdin.readline(), 'utf-8')



if __name__ == "__main__":

	tree = ET.parse('/Asfalda/framenet/fndata-asfalda/frame/Causation.xml')
	root = tree.getroot()
	xmlns = "{http://framenet.icsi.berkeley.edu}"
	Dict = {'a': '', 'c': '', 'n': '', 'v': '', 'conj': '', 'prep': ''}
	RE = {}
	File = {'a': [], 'c': [], 'n': [], 'v': [], 'conj': [], 'prep': []}


	for LU in root.findall(xmlns + 'lexUnit'):
		pos = LU.get('POS')
		name = read_trigger(LU)
		if (name not in ["pour", "comme", u"jusqu'_à", u"d'_où"]) and (pos not in ['adv']):
			Dict[pos] = Dict[pos] + name + "	|"		

	for key in Dict:
		Dict[key] = ur"" + Dict[key][:-1]
		print key + ': ' + Dict[key].encode('utf-8') + '\n'
		RE[key] = re.compile(Dict[key], re.M|re.I|re.U|re.L) 
		File[key].append(open("./text/text_" + key + "_annotated.txt", "w"))
		File[key].append(open("./text/text_" + key + "_pure.txt", "w"))
		File[key].append(open("./text/text_" + key + "_triple.txt", "w"))

	extract(Dict, RE, File)			

	for key in Dict:
		for i in {0,1,2}:
			File[key][i].close()
