from feature_extract_class import *
import os
import dill
import  copy

class storeClass:
	def __init__(self, numsent, numtok, wordfeatures, entityf, eventf, entitycoref, vso, fname):

        	self.numsentences = numsent
        	self.numtokens = numtok
		self.wordfeatures = copy.deepcopy(wordfeatures)
		self.entityfeatures = entityf
		self.eventfeatures = eventf
		self.entitycoref = entitycoref	
	        self.verbsubobj = vso
		self.filename = fname

def main():
	locn = '/home/siddharth/Downloads/gnews.bin'
	w2vmod = Word2Vec.load_word2vec_format(locn, binary=True)	

	stobjlist = []
	
	dsobjlist = []
	datapath = '/home/siddharth/backup10701/topic1'
	for f in os.listdir(datapath):
		fname = datapath + '/' + f
		temp = docStructure(fname, w2vmod)
		stobjlist.append(storeClass(temp.numsentences, temp.numtokens[:], temp.wordfeatures, temp.entityfeatures[:], temp.eventfeatures[:], temp.entitycoref[:], temp.verbsubobj[:], fname))
#		dsobjlist.append(temp)

	print stobjlist
	
	dill.dump(stobjlist, open('topic1_DS_objects.pkl', 'wb'))
		


if __name__ == "__main__":
	main()	
