#!/bin/bash

script='runTuples.sh'

touch tuples/k
rm tuples/*

for f in $@
do
	python createTrainingTuples.py "$f" &
	echo $f
done



