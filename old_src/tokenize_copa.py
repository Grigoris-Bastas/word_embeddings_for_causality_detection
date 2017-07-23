from copy import deepcopy
import pandas as pd
from codecs import open
import os
import numpy as np
import sys
import nltk
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import PlaintextCorpusReader
import re
import xml.etree.ElementTree as ET
import sys; sys.path.append('/home/irvin/Downloads/pattern-2.6')
from pattern.fr import split,lemma
from numpy import linalg as LA

def tokens_of(sentence, xfile):
	tokenizer = WordPunctTokenizer()
	M = tokenizer.tokenize(sentence)
	del M[-1]
	if "'" in M:
		M.remove("'")
	for word in M:
		xfile.write(word + '\n')
	xfile.write('\n')

	
xfile = open("./copa_tokenized.txt",'w','utf-8')
pfile = open("./copa_pure.txt",'w','utf-8')

tree = ET.parse('./copa-dev.fr.xml')
root = tree.getroot()
for item in root.findall('item'):
	i = int(item.get('id'))

	p = item.find('p').text
	a1 = item.find('a1').text
	a2 = item.find('a2').text

	pfile.write(p+'\n')
	pfile.write(a1+'\n')
	pfile.write(a2+'\n')

#	tokens_of(p, xfile)
#	tokens_of(a1, xfile)
#	tokens_of(a2, xfile)

	if i == 50:
		break

xfile.close()

