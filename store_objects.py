from feature_extract_class import *
import os
import dill
import  copy

class storeClass:
	def __init__(self, numsent, numtok, wordfeatures, entityf, eventf, entitycoref, vso, fname, em,  ev):

		self.numsentences = numsent
		self.numtokens = numtok
		self.wordfeatures = copy.deepcopy(wordfeatures)
		self.entityfeatures = entityf
		self.eventfeatures = eventf
		self.entitycoref = entitycoref
		self.verbsubobj = vso
		self.filename = fname
		self.entitymentions = em
                self.eventmentions = ev


def main():
	locn = '/home/siddharth/Downloads/gnews.bin'
	w2vmod = Word2Vec.load_word2vec_format(locn, binary=True)	

	stobjlist = []
	
	flist = []
	dsobjlist = []

	topicid = sys.argv[1]
		
	count = 1
	lst = range(1, 20)	
	lst.remove(16)
	datapath = '/home/siddharth/backup10701/topic1'
	for i in lst:
		
		fname = datapath + '/' + "data_" + topicid + "_" + str(i) + ".eecb.xml"
		temp = docStructure(fname, w2vmod)
		stobjlist.append(storeClass(temp.numsentences, temp.numtokens[:], temp.wordfeatures, temp.entityfeatures[:], temp.eventfeatures[:], temp.entitycoref[:], temp.verbsubobj[:], fname,  temp.entitymentions, temp.eventmentions))
		dsobjlist.append(temp)

	dill.dump(stobjlist, open('topic1_DS_ordered.pkl', 'wb'))


if __name__ == "__main__":
	main()	
