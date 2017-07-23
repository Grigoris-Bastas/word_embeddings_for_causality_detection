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

class MyStruct:
	def __init__(self, IDnumber, frameName):
		self.ID = IDnumber
		self.frame = frameName


def preliminary_write(df,count,Triggers,AdjL,sentNum,sentence,pureSentence):
	flag = True
	for trig in Triggers:
		if AdjL[trig.ID] and flag:
			#write sentence in file
			df[0].write(str(count)+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n'+sentence.encode('utf-8')+'\n')
			df[1].write(str(count)+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n\n')
			df[2].write(str(count)+'|'+str(sentNum)+') ')
			flag = False

	
def isolate_pure_sentence(pureSentence, lineTag):
	if lineTag[4] == 'PONCT':
		pureSentence = pureSentence[:-1] + lineTag[1] + ' '
	else:
		pureSentence = pureSentence + lineTag[1] + ' '

	return pureSentence

	
def create_adjacency_list(AdjList, Parent):
	for i in range(0, len(Parent)+1):
		AdjList.append([])
	for i in range(0, len(Parent)):
		parent = int(Parent[i][6])
		AdjList[parent].append(i+1)		

	return AdjList

def read_trigger(LU):
	name = LU.get('name')
	name = re.sub(ur"[']+","'_", name)
	name = re.sub(ur" ","_", name)
	return name.split('.')[0]


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
		
				
def extract_triple(L, AdjL, Triggers, df):

	for trig in Triggers:
		if L[trig.ID-1][7] != 'root':
			parent = int(L[trig.ID-1][6]) 
			for child in AdjL[trig.ID]:
				AdjList = deepcopy(AdjL)	#deepcopy saved me (it generates list with new id, so pop() has no effect)
				A = L[parent-1][:]
				B = L[trig.ID-1]
				C = L[child-1][:]

				sonOfParent = capture_verb_phrase(A,parent,AdjList,L,trig.ID)
		
				SonOfChild = capture_verb_phrase(C,child,AdjList,L,trig.ID)

				grandsonOfParent = capture_verb_phrase(A,sonOfParent,AdjList,L,trig.ID)

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
					df[i].write(trig.frame)
					df[i].write('\n\n\n')




def extract(RE, File):
	line = unicode(sys.stdin.readline(), 'utf-8')
	count = {'a': 0, 'c': 0, 'n': 0, 'v': 0, 'conj': 0, 'prep': 0}
	Triggers = {}
	word = ''
	sentence = ''
	pureSentence = ''
	sentNum = 0
	lineNum = 0
	pos = []

	Triggers = {key: [] for key in count} 

	while line:	
		if len(line)>1:
			sentence = sentence + line
			lineNum += 1
			lineTag = line.split('\t')
			pureSentence = isolate_pure_sentence(pureSentence, lineTag)

			#search for triggers
			#We use this "key" thing because we might detect multiple triggers of different types in the same sentence
			for frame in RE:
				for key in RE[frame]:
					trigger = RE[frame][key].search(lineTag[2])				
					if trigger:
						if lineTag[3][0] == key[0].upper(): 	#check the part-of-speech
							word = trigger				#Let's store it somewhere. 
							Triggers[key].append(MyStruct(lineNum,frame))
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
					preliminary_write(File[key], count[key], Triggers[key], AdjL, sentNum, sentence, pureSentence)
					#write triple in file
					extract_triple(L, AdjL, Triggers[key], File[key])
					

			pos = []
			lineNum = 0
			word = ''
			sentence = ''
			pureSentence = ''
			Triggers = {key: [] for key in count} 
		line = unicode(sys.stdin.readline(), 'utf-8')



if __name__ == "__main__":
	xmlns = "{http://framenet.icsi.berkeley.edu}"
	#TODO: just fill all of the list POS
	POS = ['a', 'c', 'n', 'v', 'conj', 'prep']
	Causality = ['Causation', 'Evidence', 'Explaining_the_facts', 'FR_Attributing_cause', 
		     'FR_Cause_enunciation', 'FR_Cause_to_start-Launch_process', 'FR_Contingency-Objective_influence', 
		     'FR_Reason','Make_possible_to_do', 'Preventing', 'Response']



	#dictionaries' initialisation
	regexString = {key1: {key2: '' for key2 in POS}  for key1 in Causality}
	File = {key: [] for key in POS}
	RE = {}

	
	for frame in Causality:
		tree = ET.parse('/Asfalda/framenet/fndata-asfalda/frame/' + frame + '.xml')
		root = tree.getroot()
		for LU in root.findall(xmlns + 'lexUnit'):
			pos = LU.get('POS')
			name = read_trigger(LU)
			if (name not in ["pour", "comme", u"jusqu'_à", u"d'_où"]) and (pos in POS):  #TODO: pos in POS is time consuming
				regexString[frame][pos] = regexString[frame][pos] + name + "|"		
		

	for frame in regexString:			
		RE[frame] = {}
		for pos in regexString[frame]:
			regexString[frame][pos] = ur"" + regexString[frame][pos][:-1]
			if regexString[frame][pos] == '':
				regexString[frame][pos] = "jhf kayjhfejhiu dxkjh baxkejhytyioqwuhjfebmnbx" 
			#print pos + ': ' + regexString[frame][pos].encode('utf-8') + '\n'
			RE[frame][pos] = re.compile(regexString[frame][pos], re.M|re.I|re.U|re.L) 
	
	
	for key in POS:
		File[key].append(open("./text/text_" + key + "_annotated.txt", "w"))
		File[key].append(open("./text/text_" + key + "_pure.txt", "w"))
		File[key].append(open("./text/text_" + key + "_triple.txt", "w"))
	
	extract(RE, File)			
	
	for key in POS:
		for i in {0,1,2}:
			File[key][i].close()

#	regexString = {key1: {} for key1 in Causality}
#	File = {key: [] for key in POS}
#	RE = {}
#
#	
#	for frame in Causality:
#		tree = ET.parse('/Asfalda/framenet/fndata-asfalda/frame/' + frame + '.xml')
#		root = tree.getroot()
#		for LU in root.findall(xmlns + 'lexUnit'):
#			pos = LU.get('POS')
#			name = read_trigger(LU)
#			if pos not in POS[frame]:
#				POS[frame].append(pos)
#				if (name not in ["pour", "comme", u"jusqu'_à", u"d'_où"]):
#					regexString[frame][pos] = regexString[frame][pos] + name + "	|"		
