import os
import sys
from codecs import open

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

LU = {}
V = []
f = open(sys.argv[1],'r', 'utf-8')		# ususally sys.argv[1] = wv or cv
for line in f:
        word = line.split(' ')[0]
	LU[word] = 0
        V.append(word)
del LU[u'']
V.sort()

sum = 0
count = 0
path = '/home/irvin/python_practice_thesis/corpus/times/'
for file in os.listdir(path):
	print count
	count += 1
        with open(path+file, 'r', 'utf-8') as f:
		if file in ['src','useful_garbage']:
			continue
		sum += int(f.readline())		
		next(f)
                for line in f:
                        entry = line.split()
			if entry == []:
				continue
                        times = int(entry[0])
                        word = entry[1]
                        if bin_search(V, word):
                                LU[word] += times

print sum

with open(sys.argv[1]+'_frequency.txt','w','utf-8') as out:
	out.write(str(sum)+'\n')
	for word, times in LU.iteritems():
		out.write(word+'\t'+str(times)+'\n')




#
#	T = {}
#	P = {}
#	f = open('wv','r', 'utf-8')
#	for line in f:
#		word = line.split(' ')[0]
#		P[word] = 0
#		T[word] = 0
#
#	path = '/home/irvin/python_practice_thesis/corpus/times/'
#	Vocabulary = []
#	LU = []
#	Times = {}
#	superSum = 0
#	for frwacVoc in os.listdir(path):
#		frw = open(path+frwacVoc, 'r', 'utf-8')
#		print frwacVoc
#		sum = frw.readline()
#		superSum += int(sum)
#		next (frw)
#		for lineFrwac in frw:
#			entryFrwac = lineFrwac.split()
#			LU.append(entryFrwac[1])
#			Times[entryFrwac[1]] = int(entryFrwac[0])
#		print Times['vitesse']
#
#		for word in T:
#			if bin_search(LU, u'vitesse'):
#				print word
#				T[word] += Times[word]
#
#		#for word, times in T.iteritems():	
#			#print word, times		
#
#		break	
#
#	#print LU
#		
#	if '[' > 'a':
#		print 'yes'
#
#




			
		


