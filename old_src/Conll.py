#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from codecs import open
from copy import deepcopy
import os
import numpy as np
import sys
import re
from lxml import etree
from Queue import *
##from nltk.stem.snowball import FrenchStemmer


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

def valid_xml_char_ordinal(c):
	codepoint = ord(c)
	# conditions ordered by presumed frequency
	return (
		0x20 <= codepoint <= 0xD7FF or
		codepoint in (0x9, 0xA, 0xD) or
		0xE000 <= codepoint <= 0xFFFD or
		0x10000 <= codepoint <= 0x10FFFF
		)

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


def bfs(s, AdjL, L, tID=None):
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
			if v==tID:
				continue
			Q.put(v)
			dist[v] = dist[u] + 1
			if L[v][4] in ['DET','PONCT', 'CC', 'CLO', 'CLR', 'P', 'P+D', 'PRO', 'ADJWH', 'PROREL']:
				continue
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


def xmlNP(phrase, M):	
	#stemmer = FrenchStemmer()	
	for i,word in enumerate(M):
		etree.SubElement(
			phrase, "w"+str(i), 
			word=word.word,
			lemma=word.lemma, 
			pos=word.pos2, 
			synt=word.synt, 
	#		stem=stemmer.stem(word.lemma),
			dist=str(word.dist)
			)

def xmlVP(event, verb, Suj, Obj1, Obj2):
	#stemmer = FrenchStemmer()	
	try:
		etree.SubElement(event, "Verb", lemma=verb.lemma, pos=verb.pos1)#, stem=stemmer.stem(verb.lemma))

		subject = etree.SubElement(event, "Subject", numOfWords=str(len(Suj)), phrase=' '.join([x.word for x in Suj]))
		xmlNP(subject, Suj)

		object1 = etree.SubElement(event, "Object1", numOfWords=str(len(Obj1)), phrase=' '.join([x.word for x in Obj1]))	
		xmlNP(object1, Obj1)

		object2 = etree.SubElement(event, "Object2", numOfWords=str(len(Obj2)), phrase=' '.join(x.word for x in Obj2))	
		xmlNP(object2, Obj2)
	except (TypeError,ValueError):
		return
	



def extract_triple(L, AdjL, trigName, tID, Frames, df, root):
	tr = lu(L[tID])
	if tr.parent == 0:
		return

	pa = lu(L[tr.parent],0)
	# Capture ParentPhrase
	if tr.pos2 in ['CC', 'CS', 'P'] and pa.pos1 == 'V':
		pSuj, pObj1, pObj2 = capture_verb_phrase(pa, AdjL, L, tID)
	elif tr.pos1 == 'V' and pa.pos2 == 'NC': 
		pNP = bfs(pa, AdjL, L, tID)
	else:
		return

	global phraseID
	phraseID+=1	

	#child ID
	for cID in AdjL[tID]:
		ch = lu(L[cID],0)

		# Capture ChildPhrase
		if tr.pos2 in ['P'] and ch.pos1 == 'N':	
			cNP = bfs(ch, AdjL, L, tID)
		elif tr.pos2 in ['CC', 'CS'] and ch.pos1 == 'V':
			cSuj, cObj1, cObj2 = capture_verb_phrase(ch, AdjL, L, tID)
		elif tr.pos1 == 'V':
			cNP = bfs(ch, AdjL, L, tID)
		else:
			continue

		# Print XML for 4 seed patterns
		touple = etree.SubElement(root, "tuple", id=str(phraseID), trigger=tr.lemma, frame=Frames, pos=tr.pos2, word=tr.word)
		if tr.pos2 == 'P' and ch.pos1 == 'N': 
			effect = etree.SubElement(touple, "effect", type="VP") 
			xmlVP(effect, pa, pSuj, pObj1, pObj2)
			
			cause = etree.SubElement(touple, "cause",type="NP")
			np = etree.SubElement(cause, "NP", numOfWords=str(len(cNP)), phrase=' '.join([x.word for x in cNP])) 
			xmlNP(np, cNP)

		elif tr.pos2 == 'V' or (tr.pos2 == 'VPP' and L[tID-1][2] == 'avoir'):		      
			cause = etree.SubElement(touple, "cause",type="NP")
			np = etree.SubElement(cause, "NP", numOfWords=str(len(pNP)), phrase=' '.join([x.word for x in pNP])) 
			xmlNP(np, pNP)

			effect = etree.SubElement(touple, "effect",type="NP")
			np = etree.SubElement(effect, "NP", numOfWords=str(len(cNP)), phrase=' '.join([x.word for x in cNP])) 
			xmlNP(np, cNP)

		elif tr.pos2 == 'VPP':		      
			effect = etree.SubElement(touple, "effect",type="NP")
			np = etree.SubElement(effect, "NP", numOfWords=str(len(pNP)), phrase=' '.join([x.word for x in pNP])) 
			xmlNP(np, pNP)

			cause = etree.SubElement(touple, "cause",type="NP")
			np = etree.SubElement(cause, "NP", numOfWords=str(len(cNP)), phrase=' '.join([x.word for x in cNP])) 
			xmlNP(np, cNP)

		elif tr.pos2 in ['CC', 'CS'] and ch.pos1 == 'V':
			effect = etree.SubElement(touple, "effect", type="VP") 
			xmlVP(effect, pa, pSuj, pObj1, pObj2)

			cause = etree.SubElement(touple, "cause", type="VP")
			xmlVP(cause, ch, cSuj, cObj1, cObj2)

	return	
			

def preliminary_write(df,count,sentNum,sentence,pureSentence):
	df[0].write(str(count)+'|'+str(sentNum)+') '+pureSentence+'\n'+sentence+'\n')
	df[1].write(str(count)+'|'+str(sentNum)+') '+pureSentence+'\n\n')
	df[2].write(str(count)+'|'+str(sentNum)+') ')


def extract(Triggers, File, TrPos, TrFrame, root):
	with open(sys.argv[1], 'r') as f:
		line = unicode(f.readline(), 'utf-8')
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

					# ne_verb
					for wordject in L:
						if wordject==[]:
							continue
						if wordject[2] == 'ne':
							neParent = int(wordject[6])
							if neParent!=0:
								L[neParent][2] = 'ne_'+L[neParent][2]  

					# Yep, somewhere in this sentence there is a trigger. 
					AdjL = create_adjacency_list(AdjL, L)
					for trig in Words:
						pos = TrPos[trig.name]		
						Frames = TrFrame[trig.name]
						count[pos] += 1
						preliminary_write(File[pos], count[pos], sentNum, sentence, pureSentence)
						extract_triple(L, AdjL, trig.name, trig.ID, Frames, File[pos], root)

					sentNum += 1	

				L = [[]]
				Words = []
				lineNum = 0
				sentence = pureSentence = ''

			line = unicode(f.readline(), 'utf-8')


if __name__ == "__main__":

	phraseID=0				
	POS = ['c', 'conj', 'prep', 'v']
	TrPos = {}
	TrFrame = {}
	Triggers = []
	File = {'c':[], 'conj':[], 'prep':[], 'v':[]}

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

	FileID = sys.argv[1][49:53]
	fname = './xml_extractions/extractions_' +FileID+'.xml' 
	tree = etree.ElementTree(root)
	with open(fname, 'wb') as f:
		tree.write(f, encoding='utf-8', pretty_print=True)
	
	# Close files
	for key in POS:
		for i in [0,1,2]:
			File[key][i].close()

	outputFile.close()
