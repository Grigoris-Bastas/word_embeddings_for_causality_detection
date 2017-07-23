#!/bin/bash

#./multuples.sh ~/python_practice_thesis/thesisBigData/xml_extractions/*

count=0
for f in $@
do
	echo "$f"
        python createTrainingTuples.py "$f" 
#	(( count ++ ))        
#	if (( count = 4 )); then
#		wait
#		count=0
#	fi
done

