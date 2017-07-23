#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from codecs import open
from copy import deepcopy
import os
import numpy as np
import sys
import re
import io
import xml.etree.ElementTree as ET
from itertools import islice
from numpy import linalg as LA


def cosine(a,b):
        return np.inner(a,b)/(LA.norm(a)*LA.norm(b))



w1 = sys.argv[1]
w2 = sys.argv[2]
Vocabulary = []
Vectors = []

with open('./cause-vectors.txt','r') as f: 
	next(f)
	for line in f:
		entry = deepcopy(line.split(' '))
		Vocabulary.append(entry[0])
		vector = map(float,entry[1:-1]) 
		Vectors.append(vector)


if all(x in Vocabulary for x in [w1,w2]):
	i_w1 = Vocabulary.index(w1)
	i_w2 = Vocabulary.index(w2)
	a = np.array(Vectors[i_w1])
	b = np.array(Vectors[i_w2])
	print cosine(a,b)

print cosine(np.array([1,0]), (np.array([1,0])))

	




