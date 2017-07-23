#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from codecs import open
import os
import numpy as np
import sys
import io

#python quick_tuple_mutation.py ~/python_practice_thesis/thesisBigData/tuples1705/cause-effect.txt

in_dir = sys.argv[1]

f = open(in_dir, 'r', 'utf-8')
of1 = open('/home/irvin/python_practice_thesis/thesisBigData/tuples1805_allFRcsef/cs_cause-ef_effect.txt', 'w', 'utf-8')

for i,line in enumerate(f):
	w = line.split(' ')
	w[1] = w[1][:-1]
	of1.write('cs_'+w[0]+' '+'ef_'+w[1]+'\n')
		
f.close()
of1.close()
#of2.close()
