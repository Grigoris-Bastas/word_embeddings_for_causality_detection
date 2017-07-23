#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
import os
import numpy as np
import sys
import gensim,logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname
 
    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)):
                yield line.split()

tuple_dir1 = '/home/irvin/python_practice_thesis/thesisBigData/tuples2405_allFR_dist8_csef'#tuples2305_allFR_csef'
fname1 = '/home/irvin/python_practice_thesis/thesisBigData/cs-ef_vectors_2305_allFR_dist8_300_sg0_n5'

sentences1 = MySentences(tuple_dir1) # a memory-friendly iterator
model1 = gensim.models.Word2Vec(sentences1, size=300, window=1, min_count=0, workers=4, sg=0, negative=5)
print model1
model1.save(fname1)

