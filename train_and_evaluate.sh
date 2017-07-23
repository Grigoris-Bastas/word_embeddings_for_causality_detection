#!/bin/bash

infile=$1
#outfile=$2

./myword2vecf/count_and_filter -train $infile -cvocab ./word2vecf_extractions/cv -wvocab ./word2vecf_extractions/wv -min-count 26

./myword2vecf/word2vecf -train $infile -wvocab ./word2vecf_extractions/wv -cvocab ./word2vecf_extractions/cv -output ./word2vecf_extractions/cause_vectors.txt -size 500 -negative 15 -threads 10

#python tokenize_copa.py

#cd ~/Downloads/morfette-master && morfette predict data/fr/model < /home/irvin/Dropbox/project_thesis/copa_tokenized.txt > /home/irvin/Dropbox/project_thesis/lemmatized_copa.txt

#python evaluation_copa.py
