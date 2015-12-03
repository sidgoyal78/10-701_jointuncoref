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
	opdir = sys.argv[1] 

	alltopics = [11, 2, 44, 25, 10, 4, 45, 16, 30, 27, 43, 1, 20, 35, 28, 26, 8, 18, 39, 3, 42, 13, 12, 36, 32, 38, 14, 22, 7, 19, 24, 23, 34, 9, 21, 6, 5, 40, 37, 29, 33, 31, 41]

	alldocs = {1: [6, 19, 3, 5, 8, 18, 13, 10, 2, 12, 11, 9, 15, 14, 1, 7, 4, 17], 2: [6, 3, 5, 8, 2, 11, 9, 1, 7, 4], 3: [6, 3, 5, 8, 2, 9, 1, 7, 4], 4: [6, 3, 5, 8, 13, 10, 2, 12, 11, 9, 14, 1, 7, 4], 5: [6, 3, 5, 13, 10, 2, 12, 11, 9, 14, 1, 7, 4], 6: [6, 3, 5, 8, 2, 9, 1, 7, 4], 7: [6, 3, 5, 8, 10, 2, 11, 9, 1, 7], 8: [6, 3, 5, 8, 2, 1, 7, 4], 9: [6, 3, 5, 8, 10, 2, 9, 1, 7, 4], 10: [6, 3, 5, 8, 2, 1, 7, 4], 11: [6, 3, 5, 8, 10, 2, 11, 9, 1, 7, 4], 12: [6, 19, 3, 5, 8, 18, 13, 16, 10, 2, 12, 11, 9, 15, 14, 1, 7, 4, 17], 13: [6, 19, 3, 21, 20, 5, 8, 18, 13, 16, 10, 2, 12, 11, 9, 15, 22, 14, 1, 7, 4, 17], 14: [6, 3, 5, 8, 10, 2, 9, 1, 7, 4], 16: [3, 2, 1], 18: [6, 3, 5, 8, 13, 16, 10, 2, 12, 11, 9, 15, 14, 1, 7, 4], 19: [6, 3, 5, 8, 10, 2, 12, 11, 9, 15, 14, 1, 7, 4], 20: [3, 5, 2, 1, 4], 21: [6, 3, 5, 8, 10, 2, 12, 11, 9, 1, 7, 4], 22: [6, 3, 5, 8, 2, 9, 1, 7, 4], 23: [6, 3, 5, 8, 10, 2, 9, 1, 7, 4], 24: [6, 3, 5, 8, 13, 10, 2, 12, 11, 9, 15, 14, 1, 7, 4], 25: [6, 3, 5, 8, 13, 10, 2, 12, 11, 9, 15, 14, 1, 7, 4], 26: [6, 3, 5, 8, 13, 10, 2, 12, 11, 9, 1, 7, 4], 27: [6, 3, 5, 8, 13, 16, 10, 2, 12, 11, 9, 15, 14, 1, 7, 4, 17], 28: [6, 3, 5, 8, 13, 10, 2, 12, 11, 9, 1, 7, 4], 29: [6, 3, 5, 8, 10, 2, 11, 9, 1, 7, 4], 30: [6, 3, 5, 8, 13, 10, 2, 12, 11, 9, 14, 1, 7, 4], 31: [6, 3, 5, 8, 13, 10, 2, 12, 11, 9, 14, 1, 7, 4], 32: [6, 3, 5, 8, 2, 1, 7, 4], 33: [3, 5, 2, 1, 4], 34: [6, 3, 5, 8, 13, 16, 10, 2, 12, 11, 9, 15, 14, 1, 7, 4], 35: [6, 3, 5, 8, 10, 2, 9, 1, 7, 4], 36: [6, 3, 5, 8, 2, 9, 1, 7, 4], 37: [6, 3, 5, 2, 1, 7, 4], 38: [3, 2, 1, 4], 39: [6, 3, 5, 8, 13, 10, 2, 12, 11, 9, 14, 1, 7, 4], 40: [6, 3, 5, 8, 10, 2, 9, 1, 7, 4], 41: [6, 3, 5, 8, 2, 9, 1, 7, 4], 42: [6, 3, 5, 8, 13, 10, 2, 12, 11, 9, 1, 7, 4], 43: [6, 3, 5, 8, 2, 1, 7, 4], 44: [6, 3, 5, 2, 1, 7, 4], 45: [6, 3, 5, 8, 2, 1, 7, 4]}

	
	datapath = '/home/siddharth/Downloads/10-701-ML/final_project/corpus/EECB1.0/newdata/'
	for topic in sorted(alltopics):
#	for topic in [7]:
		stobjlist = []
		for docid in sorted(alldocs[topic]):	
#		for docid in [10] :	
			filename = "data_" + str(topic) + "_" + str(docid) + ".eecb.xml"
			print "doing this filename", filename
			fpath = datapath + filename
			temp = docStructure(fpath, w2vmod)
			stobjlist.append(storeClass(temp.numsentences, temp.numtokens[:], temp.wordfeatures, temp.entityfeatures[:], temp.eventfeatures[:], temp.entitycoref[:], temp.verbsubobj[:], filename,  temp.entitymentions, temp.eventmentions))

		dill.dump(stobjlist, open(opdir + '/' + 'topic' + str(topic) + '_DS_ordered.pkl', 'wb'))
		print "finished topic", topic


if __name__ == "__main__":
	main()	
