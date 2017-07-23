#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from codecs import open
from copy import deepcopy
import os
import numpy as np
import sys
import re
import xml.etree.ElementTree as ET
from Queue import *


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

def bfs(M, s, AdjL, L, trigID, position):
	dist = []
	NV = [s]
	for u in range(1,len(AdjL)+1):
		dist.append(500)
	dist[s] = 0
	Q = Queue()
	Q.put(s)
	while not Q.empty():
		u = Q.get()

		for v in AdjL[u]:
			#if (
			#	v != trigID and 
			#	L[v-1][4] in ['NC','ADV','ADJ','VPP','VINF','P','NPP','PRO','VPR','P+D'] and
			#	L[v-1][7] in ['obj','suj','mod','ats','dep']
			#  ):
			if L[v-1][7] == 'det':
				continue
			Q.put(v)
			dist[v] = dist[u] + 1
			if position == 0:
				for j in [2,4,7]:
					M[j].insert(dist[v],L[v-1][j])

			else:
				for j in [2,4,7]:
					M[j].append(L[v-1][j])


#			print len(L)
#			min = 100
#			if AdjList[parent]:
#				V = AdjList[parent][0]
#			for v in AdjL[parent]:
#				if (
#					v != ID+1 and 
#					L[v-1][4] in ['NC','ADV','ADJ','VPP','VINF','P','NPP','PRO','VPR'] and
#					L[v-1][7] in ['obj','suj','mod','ats','dep']
#				   ):
#					if min > abs(parent-v):
#						min = abs(parent-v)
#						V = v
#			for j in [2,4,7]:
#				A[j].append(L[V-1][j])
def capture_verb_phrase(M, p, AdjL, L, trigID):				
	count = 0
	for v in AdjL[p]:
		if not 	(
			v != trigID and 
			L[v-1][4] in ['NC','ADV','ADJ','VPP','VINF','P','NPP','PRO','VPR','P+D'] and
			L[v-1][7] in ['obj','suj','mod','ats','dep','a_obj','de_obj','root']
			):
			continue

		if L[v-1][7] == 'suj' and v < p:	
			M[2].insert(0,' ')
			for j in [2,4,7]:
				M[j].insert(0,L[v-1][j])
			bfs(M, v, AdjL, L, trigID, 0)

		elif v > p and count <=1:
			count += 1
			M[2].append(' ')
			for j in [2,4,7]:
				M[j].append(L[v-1][j])
			bfs(M, v, AdjL, L, trigID, 1)

				
def extract_triple(L, AdjL, trigName, ID, Frames, df, output):
	if L[ID][7] == 'root':
		return

	parent = int(L[ID][6]) 
	if (L[ID][4] in ['CC', 'CS', 'P']) and (L[parent-1][3] != 'V'): 
			return
	
	for child in AdjL[ID+1]:

		if (L[ID-1][4] == 'P') and (L[child-1][3] != 'N'):
			continue

		if (L[ID-1][4] in ['CC', 'CS']) and (L[child-1][3] != 'V'):
			continue
			
	

		#TODO: avoid reappearance of the same words like parent\n parent\n parent\n
		#TODO:read about syntactic trees
		#TODO: if subject->up if object->down
		StopWords = [u"être","avoir","pas","ne","l","l'","trop","plus","beaucoup","aussi","encore","faire","aller","venir",
		u"très","que","tout","devoir","rendre",u"même","non","ainsi","falloir","juste"]
		AdjList = deepcopy(AdjL)	#deepcopy saved me (it generates list with new id, so pop() has no effect)
		A = deepcopy([[x] for x in L[parent-1]])
		B = deepcopy(L[ID])
		C = deepcopy([[x] for x in L[child-1]])


		capture_verb_phrase(A, parent, AdjList, L, ID+1)

		if (L[ID][4] in ['P']):	
			bfs(C, child, AdjList, L, ID+1, 1)
		elif (L[ID][4] in ['CC', 'CS']):
			capture_verb_phrase(C, child, AdjList, L, ID+1)


		df[0].write("Parents' sons: " + str(AdjL[parent]) + "	Children's sons: " + str(AdjL[child]))	
		df[0].write('\n\n')
		for i in [0,1,2]:
			#if (A[3][0] in ['V','N','A']) and (C[3][0] in ['V','N']): 
			df[i].write(" \n")
			df[i].write('~'.join(A[2])+'{'+'~'.join(A[4])+'|'+'~'.join(A[7])+'}\n\n')
			df[i].write(B[2]+'{'+B[4]+'|'+B[7]+'}\n\n')
			df[i].write('~'.join(C[2])+'{'+'~'.join(C[4])+'|'+'~'.join(C[7])+'}\n\n')
			df[i].write(Frames)
			df[i].write('\n\n\n')
				
		output.write('~'.join(A[2])+'\n')
		output.write('~'.join(C[2])+'\n\n')

				

#		if (A[3] in ['V','N','A']) and (C[3] in ['V','N']):
#			for effet, pos in zip(A[2].split('~'), A[4].split('~')):
#				if (effet not in StopWords) and (pos != 'ADV') and not(effet[0].isdigit()):
#					for cause, pos in zip(C[2].split('~'), C[4].split('~')):
#						if (cause not in StopWords) and (pos != 'ADV') and not(cause[0].isdigit()):
#							if effet[:2] == "l'":
#								effet = effet[2:]
#							if cause[:2] == "l'":
#								cause = cause[2:]
#							output.write((effet+' '+cause+'\n'))
	

def preliminary_write(df,count,sentNum,sentence,pureSentence):
	df[0].write(str(count)+'|'+str(sentNum)+') '+pureSentence+'\n'+sentence+'\n')
	df[1].write(str(count)+'|'+str(sentNum)+') '+pureSentence+'\n\n')
	df[2].write(str(count)+'|'+str(sentNum)+') ')


def extract(Triggers, File, TrPos, TrFrame, outputFile):
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
			stem = line.split('\t',3)[2]
			#******* search for triggers *******#
			if bin_search(Triggers, stem):
				Words.append(MyStruct(lineNum, stem))				
			#******* search for triggers *******#
			lineNum += 1
					
		else:
			#A whole sentence is extracted 
			if Words:
				wordject = sentence.split('\n')
				for i in range(0,lineNum):
					linetag = wordject[i].split('\t')
					L.append(linetag)
					pureSentence = isolate_pure_sentence(pureSentence, linetag)

				#Yep, somewhere in this sentence there is a trigger. 
				AdjL = create_adjacency_list(AdjL, L)
				for trig in Words:
					pos = TrPos[trig.name]		
					Frames = TrFrame[trig.name]
					count[pos] += 1
					preliminary_write(File[pos], count[pos], sentNum, sentence, pureSentence)
					extract_triple(L, AdjL, trig.name, trig.ID, Frames, File[pos], outputFile)
					

				sentNum += 1	

			L = []
			Words = []
			lineNum = 0
			sentence = pureSentence = ''

		line = unicode(sys.stdin.readline(), 'utf-8')




if __name__ == "__main__":

	POS = ['c', 'conj', 'prep']
	TrPos = {}
	TrFrame = {}
	Triggers = []
	File = {'c':[], 'conj':[], 'prep':[]}

	f = open('./tagged_list_of_triggers.txt','r')
	for line in f:
		entry = line.split()
		trName = entry[0].decode('utf-8')
		Triggers.append(trName)
		TrPos[trName] = entry[1]
		TrFrame[trName] = entry[2]
	f.close()

	# Open files to write
	for key in POS:
		File[key].append(open("./text/text_" + key + "_annotated.txt", 'w', 'utf-8'))
		File[key].append(open("./text/text_" + key + "_pure.txt", 'w', 'utf-8'))
		File[key].append(open("./text/text_" + key + "_triple.txt", 'w', 'utf-8'))

	outputFile = open("./training_data.txt",'a', 'utf-8')
	
	#########################################
	extract(Triggers, File, TrPos, TrFrame, outputFile)			
	#########################################
	
	# Close files
	for key in POS:
		for i in [0,1,2]:
			File[key][i].close()

	outputFile.close()
