#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from codecs import open
from copy import deepcopy
import os
import numpy as np
import sys
import re
##import xml.etree.ElementTree as ET
from lxml import etree

from Queue import *
from nltk.stem.snowball import FrenchStemmer


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

class lu:
	def __init__(self, X, dist=None, word=None, lemma=None, pos1=None, pos2=None, synt=None, parent=None):
		if type(X) == list:
			self.id = int(X[0])
			self.word = X[1]
			self.lemma = X[2]
			self.pos1 = X[3]
			self.pos2 = X[4]
			self.parent = int(X[6])
			self.synt = X[7]
			self.dist = dist
		else:		
			self.id = int(X)
			self.word = word
			self.lemma = lemma
			self.pos1 = pos1
			self.pos2 = pos2
			self.parent = int(parent)
			self.synt = synt
			self.dist = dist

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

	
def create_adjacency_list(AdjList, L):
	AdjList = []
	for i in range(0, len(L)):
		AdjList.append([])
	for i in range(1, len(L)):
		parent = int(L[i][6])
		AdjList[parent].append(i)		

	return AdjList

def read_trigger(LU):
	name = LU.get('name')
	name = re.sub(ur"[']+","'_", name)
	name = re.sub(ur" ","_", name)
	return name.split('.')[0]

def auxiliary_write(df,output, A, B, C, Frames, AdjL, pID, cID):
		df[0].write("Parents' sons: " + str(AdjL[pID]) + "	Children's sons: " + str(AdjL[cID]))	
		df[0].write('\n\n')
		for i in [0,1,2]:
			df[i].write("\n")
			df[i].write('~'.join(A[2])+'{'+'~'.join(A[4])+'|'+'~'.join(A[7])+'}\n\n')
			df[i].write(B[2]+'{'+B[4]+'|'+B[7]+'}\n\n')
			df[i].write('~'.join(C[2])+'{'+'~'.join(C[4])+'|'+'~'.join(C[7])+'}\n\n')
			df[i].write(Frames)
			df[i].write('\n\n\n')
		output.write('~'.join(A[2])+'\n')
		output.write('~'.join(C[2])+'\n\n')

		StopWords = [u"être","avoir","pas","ne","l","l'","trop","plus","beaucoup","aussi","encore","faire","aller","venir",
		u"très","que","tout","devoir","rendre",u"même","non","ainsi","falloir","juste"]

def bfs(s, AdjL, L):
	dist = []
	for u in range(1,len(AdjL)+1):
		dist.append(500)
	dist[s.id] = 0
	M = [s]
	Q = Queue()
	Q.put(s.id)
	while not Q.empty():
		u = Q.get()
		for v in AdjL[u]:
			if L[v][4] in ['DET','PONCT']:
				continue
			Q.put(v)
			dist[v] = dist[u] + 1
			M.append(lu(L[v],dist[v]))
	return M		


def capture_verb_phrase(vrb, AdjL, L, tID):				
	count = 0
	S=[]
	O1=[]
	O2=[]
	for u in AdjL[vrb.id]:

		if u == tID or L[u][4] in ['DET', 'PONCT']:
			continue

		if L[u][7] == 'suj' and u < vrb.id:	
			S = bfs(lu(L[u],0), AdjL, L)

		elif u > vrb.id and count <=1:
			if count == 0:
				O1 = bfs(lu(L[u],0), AdjL, L)
			elif count <= 1:	
				O2 = bfs(lu(L[u],0), AdjL, L)
			count += 1

	return S, O1, O2	

def xmlVP(event, verb, Suj, Obj1, Obj2, stemmer):
	etree.SubElement(event, "Verb", lemma=verb.lemma, pos=verb.pos1, stem=stemmer.stem(verb.lemma))
	subject = etree.SubElement(event, "Subject", numOfWords=str(len(Suj)), subjPhrase=' '.join([x.word for x in Suj]))
	for i,word in enumerate(Suj):
		etree.SubElement(subject, "w"+str(i), lemma=word.lemma, pos=word.pos2, 
		      synt=word.synt, stem=stemmer.stem(word.lemma), dist=str(word.dist))
	object1 = etree.SubElement(event, "Object1", numOfWords=str(len(Obj1)), obj1Phrase=' '.join([x.word for x in Obj1]))	
	for i,word in enumerate(Obj1):
		etree.SubElement(object1, "w"+str(i), lemma=word.lemma, pos=word.pos2, 
		      synt=word.synt, stem=stemmer.stem(word.lemma), dist=str(word.dist))
	object2 = etree.SubElement(event, "Object2", numOfWords=str(len(Obj2)), obj2Phrase=' '.join([x.word for x in Obj2]))	
	for i,word in enumerate(Obj2):
		etree.SubElement(object2, "w"+str(i), lemma=word.lemma, pos=word.pos2, 
		      synt=word.synt, stem=stemmer.stem(word.lemma), dist=str(word.dist))


#if x.pos2=='NPP':
#	if x.synt=='suj':
#		x.word='cln'
#	elif x.synt=='obj':	
#		x.word='lui'
				
def extract_triple(L, AdjL, trigName, tID, Frames, df, root, sentNum):
	stemmer = FrenchStemmer()	
	tr = lu(L[tID])
	if tr.parent == 0:
		return
	pa = lu(L[tr.parent])
	if (tr.pos2 in ['CC', 'CS', 'P'] and pa.pos1 != 'V'): 
		return


	#Capture Effect
	pSuj, pObj1, pObj2 = capture_verb_phrase(pa, AdjL, L, tID)
	
	#child ID
	for cID in AdjL[tID]:
		ch = lu(L[cID],0)

		#Capture Cause
		if (tr.pos2 in ['P'] and ch.pos1 == 'N'):	
			NP = bfs(ch, AdjL, L)
		elif (tr.pos2 in ['CC', 'CS'] and ch.pos1 == 'V'):
			cSuj, cObj1, cObj2 = capture_verb_phrase(ch, AdjL, L, tID)
		else:
			continue

		touple = etree.SubElement(root, "tuple", id=str(sentNum), trigger=tr.lemma, frame=Frames, pos=tr.pos2)
		#Print Effect
		effect = etree.SubElement(touple, "effect", type="VP") 
		xmlVP(effect, pa, pSuj, pObj1, pObj2, stemmer)
		#Print Cause
		if (tr.pos2 in ['P'] and ch.pos1 == 'N'):	
			cause = etree.SubElement(touple, "cause", type="NP")
			for i,word in enumerate(NP):
				etree.SubElement(cause, "w"+str(i), lemma=word.lemma, pos=word.pos2, synt=word.synt,
				      stem=stemmer.stem(word.lemma),dist=str(word.dist))
		elif (tr.pos2 in ['CC', 'CS'] and ch.pos1 == 'V'):
			cause = etree.SubElement(touple, "cause", type="VP")
			xmlVP(cause, ch, cSuj, cObj1, cObj2, stemmer)


	return	
			

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


def extract(Triggers, File, TrPos, TrFrame, root):
	line = unicode(sys.stdin.readline(), 'utf-8')
	count = {'a': 0, 'c': 0, 'n': 0, 'v': 0, 'conj': 0, 'prep': 0}
	sentence = pureSentence = ''
	sentNum = lineNum = 0
	L = [[]]
	Words = []
	AdjL = []
	while line:	
		# Extract a sentence
		if len(line)>1:
			lineNum += 1
			sentence = sentence + line
			lemma = line.split('\t',3)[2]
			#******* search for triggers *******#
			if bin_search(Triggers, lemma):
				Words.append(MyStruct(lineNum, lemma))				
			#******* search for triggers *******#
					
		else:
			# A whole sentence is extracted 
			if Words:
				wordject = sentence.split('\n')
				for i in range(0,lineNum):
					linetag = wordject[i].split('\t')
					L.append(linetag)
					pureSentence = isolate_pure_sentence(pureSentence, linetag)

				# Yep, somewhere in this sentence there is a trigger. 
				AdjL = create_adjacency_list(AdjL, L)
				for trig in Words:
					pos = TrPos[trig.name]		
					Frames = TrFrame[trig.name]
					count[pos] += 1
					preliminary_write(File[pos], count[pos], sentNum, sentence, pureSentence)
					extract_triple(L, AdjL, trig.name, trig.ID, Frames, File[pos], root, sentNum)

				sentNum += 1	

			L = [[]]
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



	root = etree.Element("root")	


	#########################################
	extract(Triggers, File, TrPos, TrFrame, root)			
	#########################################

	fname = 'extractions.xml' 
	tree = etree.ElementTree(root)
	with open(fname, 'wb') as f:
		tree.write(f, encoding='utf-8', pretty_print=True)

	
	# Close files
	for key in POS:
		for i in [0,1,2]:
			File[key][i].close()

	outputFile.close()
