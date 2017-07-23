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
	def __init__(self, IDnumber, Name):
		self.ID = IDnumber
		self.name = Name

def bin_search(L, target):
	min = 0
	max = len(L) - 1
	while min <= max:
		avg = (min+max)/2
		if L[avg] > target:
			max =  avg-1
		elif L[avg] < target:
			min = avg+1
		else:
			return True
	return False
	
def isolate_pure_sentence(pureSentence, lineTag):
	if lineTag[4] == 'PONCT':
		pureSentence = pureSentence[:-1] + lineTag[1] + ' '
	else:
		pureSentence = pureSentence + lineTag[1] + ' '

	return pureSentence

	
def create_adjacency_list(AdjList, Parent):
	AdjList = []
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


def capture_vicinity(A,v,AdjL,L,trigID):
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
		
				
def extract_triple(L, AdjL, trigName, ID, Frames, df):
#TODO
	if L[ID][7] != 'root':
		parent = int(L[ID][6]) 
		for child in AdjL[ID+1]:
			AdjList = deepcopy(AdjL)	#deepcopy saved me (it generates list with new id, so pop() has no effect)
			A = deepcopy(L[parent-1])
			B = deepcopy(L[ID])
			C = deepcopy(L[child-1])

			sonOfParent = capture_vicinity(A, parent, AdjList, L, ID)
			SonOfChild = capture_vicinity(C, child, AdjList, L, ID)
			grandsonOfParent = capture_vicinity(A, sonOfParent, AdjList, L, ID)

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
				for frame in Frames:
					df[i].write(frame + "/")
				df[i].write('\n\n\n')


def preliminary_write(df,count,sentNum,sentence,pureSentence):
	df[0].write(str(count)+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n'+sentence.encode('utf-8')+'\n')
	df[1].write(str(count)+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n\n')
	df[2].write(str(count)+'|'+str(sentNum)+') ')


def extract(Triggers, File, triggerPos, triggerFrame):
	line = unicode(sys.stdin.readline(), 'utf-8')
	count = {'a': 0, 'c': 0, 'n': 0, 'v': 0, 'conj': 0, 'prep': 0}
	sentence = pureSentence = ''
	sentNum = lineNum = 0
	L = []
	Words = []
	AdjL = []
	while line:	
		# Extract a sentence
		if len(line)>1:
			sentence = sentence + line
			Wordject = line.split('\t')
			L.append(Wordject) 			#list of sentence's wordjects(=word&tags)
			pureSentence = isolate_pure_sentence(pureSentence, Wordject)
			#******* search for triggers *******#
			if bin_search(Triggers,Wordject[2]):
				Words.append(MyStruct( lineNum, Wordject[2] ))				
			#******* search for triggers *******#
			lineNum += 1
					
		else:
			#A whole sentence is extracted 
			if Words:
				#Yep, somewhere in this sentence there is a trigger. 
				AdjL = create_adjacency_list(AdjL, L)

					#for trig in Words:
					#	print trig.name

				for trig in Words:
					if len(Words) > 1:
						print triggerPos[trig.name]
						print sentNum
						print trig.name
						print '\n'
					pos = triggerPos[trig.name]		
					Frames = triggerFrame[trig.name]
					count[pos] += 1
					preliminary_write(File[pos], count[pos], sentNum, sentence, pureSentence)
					extract_triple(L, AdjL, trig.name, trig.ID, Frames, File[pos])

				sentNum += 1	

			L = []
			Words = []
			lineNum = 0
			sentence = pureSentence = ''

		line = unicode(sys.stdin.readline(), 'utf-8')






if __name__ == "__main__":

	xmlns = "{http://framenet.icsi.berkeley.edu}"
	POS = ['a', 'c', 'n', 'v', 'conj', 'prep']
	Causality = ['Causation', 'Evidence', 'Explaining_the_facts', 'FR_Attributing_cause', 
		     'FR_Cause_enunciation', 'FR_Cause_to_start-Launch_process', 'FR_Contingency-Objective_influence', 
		     'FR_Reason','Make_possible_to_do', 'Preventing', 'Response']

	triggerPos = {}
	triggerFrame = {}
	Names = {}
	Triggers = []

	regexString = ''
	File = {key: [] for key in POS}
	
	# Extract trigger names, their pos and their frame by xml ASFALDA FrameNet files. Create a long trigger regex.
	for frame in Causality:
		tree = ET.parse('/Asfalda/framenet/fndata-asfalda/frame/' + frame + '.xml')
		root = tree.getroot()
		Names[frame] = []
		for LU in root.findall(xmlns + 'lexUnit'):
			pos = LU.get('POS')
			name = read_trigger(LU)
			if (name not in ["pour", "comme", u"jusqu'_à", u"d'_où","selon"]) and (pos in POS):  
				#regexString = regexString + name  + r'\t|'		
				#print regexString
				Triggers.append(name)
				triggerPos[name] = pos
				Names[frame].append(name)
				triggerFrame[name] = []

	for frame in Causality:
		for name in Names[frame]:
			triggerFrame[name].append(frame)


	print len(Triggers)
	sorted(Triggers)		

	#regexString = ur"" + regexString[:-1]
	#RE = re.compile(regexString, re.M|re.I|re.U|re.L) 
	
	# Open files to write
	for key in POS:
		File[key].append(open("./text2/text_" + key + "_annotated.txt", "w"))
		File[key].append(open("./text2/text_" + key + "_pure.txt", "w"))
		File[key].append(open("./text2/text_" + key + "_triple.txt", "w"))
	
	#################
	extract(Triggers, File, triggerPos, triggerFrame)			
	#################
	
	# Close files
	for key in POS:
		for i in {0,1,2}:
			File[key][i].close()

