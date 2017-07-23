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

def read_trigger(LU):
        name = LU.get('name')
	name = re.sub(ur"[']+","'_", name)
        name = re.sub(ur" ","_", name)
        return name.split('.')[0]

xfile = open("./tagged_list_of_triggers.txt","w")
xmlns = "{http://framenet.icsi.berkeley.edu}"
Nouns = ["aboutissement", "cause", u"conséquence", "raison", u"résultat"]
Verbs = ["aboutir", "causer", "infliger", u"provoquer","occasioner", "induire",u"déclencher"]
POS = ['c', 'conj', 'prep','v']
Ambiguous = ["pour", "comme", u"jusqu'_à", u"d'_où","selon","sinon"]
Causality = ['Causation', 'Evidence', 'Explaining_the_facts', 'FR_Attributing_cause', 
	     'FR_Cause_enunciation', 'FR_Cause_to_start-Launch_process', 'FR_Contingency-Objective_influence', 
	     'FR_Reason','Make_possible_to_do', 'Preventing', 'Response','FR_Means_for_purpose']

TrPos = {}
TrFrame = {}
Aux = {}
Triggers = []

# Extract trigger names, their pos and their frame by xml ASFALDA FrameNet files. Create a long trigger regex.
for frame in Causality:
	tree = ET.parse('/Asfalda/framenet/fndata-asfalda/frame/' + frame + '.xml')
	root = tree.getroot()
	Aux[frame] = []
	for LU in root.findall(xmlns + 'lexUnit'):
		pos = LU.get('POS')
		name = read_trigger(LU)
		#TODO: sinon
		if pos not in POS:
			continue
		if pos == 'v':
			if name not in Verbs:
				continue
		else:
			if name in Ambiguous:
				continue
		#if (name not in ["pour", "comme", u"jusqu'_à", u"d'_où","selon","sinon"]) and ((pos in POS)):
		# or (pos == 'v' and (name in Verbs))or (pos=='n' and (name in Nouns))):
		Aux[frame].append(name)
		if (name not in Triggers):
			Triggers.append(name)
			TrPos[name] = pos
			TrFrame[name] = []

for frame in Causality:
	for name in Aux[frame]:
		TrFrame[name].append(frame)

Triggers.sort()         

entry = ''
for trig in Triggers:
	entry = trig + '\t' + TrPos[trig] + '\t'
	for frame in TrFrame[trig]:
		entry = entry + frame + '/'
	entry = entry + '\n'
	xfile.write( entry.encode('utf-8') )

xfile.close()
