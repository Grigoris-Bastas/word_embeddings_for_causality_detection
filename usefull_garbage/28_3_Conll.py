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


#	|--> read_trigger
# main--|
#	|--> extract--|--> isolate_pure_sentence
#		      |--> extract_triple ---------> capture_syntactic_children
#		      |--> preliminary_write
#		      |--> bin_search
#		      |--> create_adjacency_list

class MyStruct:
	def __init__(self, IDnumber, Name):
		self.ID = IDnumber
		self.name = Name

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
	if v > 0:	#check validity of vertex (maybe it is -1)
		while AdjL[v]:
			child = AdjL[v].pop()
			if child!=trigID and (L[child-1][4] in ['NC','ADV','ADJ','VPP','VINF']):
				if L[child-1][7] == 'obj':
					for j in [2,4,7]:	
						A[j] = A[j] + '~' + L[child-1][j]
					break

				elif L[child-1][7] == 'suj':	
					for j in [2,4,7]:
						A[j] = L[child-1][j] + '~' + A[j]
					break

				elif (L[child-1][7] in ['mod', 'ats']) and (child <= v+10 and child >= v-10):
					for j in [2,4,7]:	
						A[j] = A[j] + '~' + L[child-1][j]
					break
			elif child == trigID:
				child = -1
	return child	
		
				
def extract_triple(L, AdjL, trigName, ID, Frames, df, output):
	if L[ID][7] != 'root':
		parent = int(L[ID][6]) 
		for child in AdjL[ID+1]:
			AdjList = deepcopy(AdjL)	#deepcopy saved me (it generates list with new id, so pop() has no effect)
			A = deepcopy(L[parent-1])
			B = deepcopy(L[ID])
			C = deepcopy(L[child-1])

			sonOfParent = capture_vicinity(A, parent, AdjList, L, ID+1)
			SonOfChild = capture_vicinity(C, child, AdjList, L, ID+1)
			grandsonOfParent = capture_vicinity(A, sonOfParent, AdjList, L, ID+1)

			df[0].write("Parents' sons: " + str(AdjL[parent]) + "	Children's sons: " + str(AdjL[child]))	
			df[0].write('\n\n')
			for i in [0,1,2]:
				if (A[3] in ['V','N','A']) and (C[3] in ['V','N']): 
					df[i].write("------->  ")

					df[i].write((A[2]+'{'+A[4]+'|'+A[7]+'}\t\t').encode('utf-8'))
					df[i].write((B[2]+'{'+B[4]+'|'+B[7]+'}\t\t').encode('utf-8'))
					df[i].write((C[2]+'{'+C[4]+'|'+C[7]+'}\t\t').encode('utf-8'))
					for frame in Frames:
						df[i].write(frame + "/")
					df[i].write('\n\n\n')

			if (A[3] in ['V','N','A']) and (C[3] in ['V','N']): 
				for effet in A[2].split('~'):
					for cause in C[2].split('~'):
						output.write((effet+' '+cause+'\n').encode('utf-8'))


def preliminary_write(df,count,sentNum,sentence,pureSentence):
	df[0].write(str(count)+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n'+sentence.encode('utf-8')+'\n')
	df[1].write(str(count)+'|'+str(sentNum)+') '+pureSentence.encode('utf-8')+'\n\n')
	df[2].write(str(count)+'|'+str(sentNum)+') ')


def extract(Triggers, File, triggerPos, triggerFrame, outputFile):
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
			if bin_search(Triggers, Wordject[2]):
				Words.append(MyStruct(lineNum, Wordject[2]))				
			#******* search for triggers *******#
			lineNum += 1
					
		else:
			#A whole sentence is extracted 
			if Words:
				#Yep, somewhere in this sentence there is a trigger. 
				AdjL = create_adjacency_list(AdjL, L)
				for trig in Words:
					pos = triggerPos[trig.name]		
					Frames = triggerFrame[trig.name]
					count[pos] += 1
	#				preliminary_write(File[pos], count[pos], sentNum, sentence, pureSentence)
					extract_triple(L, AdjL, trig.name, trig.ID, Frames, File[pos], outputFile)

				sentNum += 1	

			L = []
			Words = []
			lineNum = 0
			sentence = pureSentence = ''

		line = unicode(sys.stdin.readline(), 'utf-8')




if __name__ == "__main__":

	xmlns = "{http://framenet.icsi.berkeley.edu}"
	Nouns = ["aboutissement", "cause", u"conséquence", "raison", "résultat"]
	Verbs = ["aboutir", "causer", "faire_suite", u"provoquer", u"résulter"]
	POS = ['a', 'c', 'conj', 'prep']
	POS2 = ['a', 'c', 'n', 'v', 'conj', 'prep']
	Causality = ['Causation', 'Evidence', 'Explaining_the_facts', 'FR_Attributing_cause', 
		     'FR_Cause_enunciation', 'FR_Cause_to_start-Launch_process', 'FR_Contingency-Objective_influence', 
		     'FR_Reason','Make_possible_to_do', 'Preventing', 'Response']

	triggerPos = {}
	triggerFrame = {}
	Names = {}
	Triggers = []

	regexString = ''
	#File = {key: [] for key in POS2}
	File = {'a':[], 'c':[], 'conj':[], 'prep':[]}

	# Extract trigger names, their pos and their frame by xml ASFALDA FrameNet files. Create a long trigger regex.
	for frame in Causality:
		tree = ET.parse('/Asfalda/framenet/fndata-asfalda/frame/' + frame + '.xml')
		root = tree.getroot()
		Names[frame] = []
		for LU in root.findall(xmlns + 'lexUnit'):
			pos = LU.get('POS')
			name = read_trigger(LU)
#			print name,
			#TODO: sinon
			if (name not in ["pour", "comme", u"jusqu'_à", u"d'_où","selon","sinon"]) and ((pos in POS)):# or (pos == 'v' and (name in Verbs))or (pos=='n' and (name in Nouns))):
				Triggers.append(name)
				triggerPos[name] = pos
				Names[frame].append(name)
				triggerFrame[name] = []
	

	for frame in Causality:
		for name in Names[frame]:
			triggerFrame[name].append(frame)

	Triggers.sort()		
	
	# Open files to write
	for key in POS2:
		File[key].append(open("./text/text_" + key + "_annotated.txt", 'a'))
		File[key].append(open("./text/text_" + key + "_pure.txt", 'a'))
		File[key].append(open("./text/text_" + key + "_triple.txt", 'a'))

	outputFile = open("./input/input.txt",'a')
	
	#########################################
	extract(Triggers, File, triggerPos, triggerFrame, outputFile)			
	#########################################
	
	# Close files
	for key in POS2:
		for i in [0,1,2]:
			File[key][i].close()

	outputFile.close()
