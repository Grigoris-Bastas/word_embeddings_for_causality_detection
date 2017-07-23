from nltk.corpus import PlaintextCorpusReader

coprus_root = '/home/irvin/Dropbox/Thesis'

wordlists = PlaintextCorpusReaders(corpus_root,['xaa','frwac_1134.parsed.marked'])

wordlists.fileids()	#show the files

xaa = wordlist.words('xaa')	

len(xaa)	#show the number of chars in xaa
len(wordlists.raw('xaa'))

xaa_sentences = wordlists.sents('xaa')

longest_len = max([len(s) for s in xaa_sentences])

