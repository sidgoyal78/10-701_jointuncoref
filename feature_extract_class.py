from xml.dom import minidom
import snap
import sys
import sexpdata
import numpy as np
from nltk.corpus import wordnet as wn
from gensim.models import Word2Vec
from collections import OrderedDict as OD
from construct_parse_tree import Node, ParseTree
#For the wordnet, POS, class, dependency relation, and word2vec representation features
from feat_wordnet_pos_class import get_wordnet_feat, get_pos_feat, get_class_feat, get_dependency_rellabel, get_word2vec_feat


########################################

class entityMention:
	def __init__(self, txt, sentid, start, end, head):
		self.txt = txt
		self.sentid = sentid
		self.start = start
		self.end = end
		self.head = head
		
########################################

class eventMention:
	def __init__(self, txt, sentid, start, end, head):
		self.txt = txt
		self.sentid = sentid
		self.start = start
		self.end = end
		self.head = head

########################################

class docStructure:
	xmldoc = None
	wordfeatures = None
	numsentences = None
	numtokens = None
	parsetrees = None
	dependgraphs = None
	entitymentions = None
	entitycoref = None
	eventmentions = None
	verbsubobj = None
	w2vmodel = None
	eventfeatures = None
	entityfeatures = None	


	def __init__(self, fname, w2vname=None):
		self.xmldoc = minidom.parse(fname)
		self.wordfeatures = {}
		self.parsetrees = {}
		self.dependgraphs = {}
		sentencelist = self.xmldoc.getElementsByTagName('sentences')[0].getElementsByTagName('sentence')
		self.numsentences = len(sentencelist)
		self.numtokens = []

		for sent in sentencelist:
			sentenceid = int(sent.getAttribute('id'))
			tokenlist = sent.getElementsByTagName('token')			
			self.numtokens.append(len(tokenlist))
			for tok in tokenlist:
				tokenid = int(tok.getAttribute('id'))	
				word = tok.getElementsByTagName('word')[0] 		#only one word is present per token	
				lemma = tok.getElementsByTagName('lemma')[0] 	#only one lemma is present per token	
				pos = tok.getElementsByTagName('POS')[0] 		#only one pos tag is present per token	
				self.wordfeatures[(sentenceid, tokenid)] = [word.firstChild.data, lemma.firstChild.data, pos.firstChild.data]

			deplabels = {}
			depgraph = snap.TNGraph.New()
			for nid in range(self.numtokens[-1] + 1):	#One additional 'Root' node added to token nodes
				depgraph.AddNode(nid)
			basicdep = sent.getElementsByTagName('dependencies')[0]
			for dep in basicdep.getElementsByTagName('dep'):
				srcid = int(dep.getElementsByTagName('governor')[0].getAttribute('idx'))
				dstid = int(dep.getElementsByTagName('dependent')[0].getAttribute('idx'))
				depgraph.AddEdge(srcid,dstid)
				deplabels[(srcid,dstid)] = dep.getAttribute('type')
			self.dependgraphs[sentenceid] = (depgraph, deplabels)

			parstr = sent.getElementsByTagName('parse')[0].firstChild.data
			partreeobj = ParseTree(parstr, self.numtokens[-1])
			self.parsetrees[sentenceid] = partreeobj  #For getting the depth call partreeobj.get_depth(<tokenid>)

		self.get_entity_mentions()
		self.get_event_mentions()
		self.w2vmodel = w2vname
		self.get_verb_subject_object_relations()
		
		self.get_entity_mention_features()
		self.get_event_mention_features()


	def get_entity_mentions(self):
		itemlist = self.xmldoc.getElementsByTagName('coreference')
		self.entitymentions = []
		#List of lists - each nested list indicates the indices of coreferent entities in entitymentions
		self.entitycoref = []
		#Exclude first item as coreference tags are nested
		for i in itemlist[1:]:
			corefmentions = i.getElementsByTagName('mention')
			corefcons = []
			for m in corefmentions:
				txt = m.getElementsByTagName('text')[0].firstChild.data
				sentid = int(m.getElementsByTagName('sentence')[0].firstChild.data)
				start = int(m.getElementsByTagName('start')[0].firstChild.data)
				end = int(m.getElementsByTagName('end')[0].firstChild.data)
				head = int(m.getElementsByTagName('head')[0].firstChild.data)	
				corefcons.append(len(self.entitymentions))
				self.entitymentions.append(entityMention(txt,sentid,start,end,head))
			self.entitycoref.append(corefcons)


	def get_event_mentions(self):
		eventpostags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
		lemmatoignore = ['have', 'be', 'seem']
		self.eventmentions = []
		
		for sentid in range(1, self.numsentences + 1):  # 1-indexing followed in the hashmap
			ntok = self.numtokens[sentid - 1]  # as the list is 0-indexed
			flag = False	#Whether previous words were verbs
			for tokid in range(1, ntok + 1):
				if self.wordfeatures[(sentid,tokid)][2] in eventpostags and self.wordfeatures[(sentid,tokid)][1] not in lemmatoignore:
					if flag == False:
						start = tokid
						end = -1
						tempwlist = []
						tempwlist.append(self.wordfeatures[(sentid,tokid)][0])
						flag = True
					else:
						tempwlist.append(self.wordfeatures[(sentid,tokid)][0])
				else:
					if flag == True:
						end = tokid
						head = self.gen_event_mention_head(sentid,start,end)
						txt = " ".join(tempwlist)
						self.eventmentions.append(eventMention(txt,sentid,start,end,head))	
						flag = False

			if flag == True:
				end = ntok + 1
				head = self.gen_event_mention_head(sentid,start,end)
				txt = " ".join(tempwlist)
				self.eventmentions.append(eventMention(txt,sentid,start,end,head))
	

	def gen_event_mention_head(self,sentid,starttokid,endtokid):
		idvec = snap.TIntV()
		for x in range(starttokid,endtokid):
			idvec.Add(x)
		subgraph = snap.GetSubGraph(self.dependgraphs[sentid][0],idvec)
		for x in range(endtokid-1,starttokid-1,-1):
			if subgraph.GetNI(x).GetInDeg() == 0:
				return x


	def get_verb_subject_object_relations(self):
		self.verbsubobj = []
		for ind,evemen in enumerate(self.eventmentions):
			vsotup = [ind,-1,-1]
			sid = evemen.sentid
			(depgraph,deplabels) = self.dependgraphs[sid]
			vtid = evemen.head
			for x in depgraph.GetNI(vtid).GetOutEdges():
				if deplabels[(vtid,x)] == 'nsubj':
					#Lookup index of token id x in sentence id sid self.entitymentions (if exists)
					for i,entmen in enumerate(self.entitymentions):
						if entmen.sentid == sid:
							if entmen.start <= x and x < entmen.end:
								vsotup[1] = i		
				elif deplabels[(vtid,x)] == 'dobj':
					for i,entmen in enumerate(self.entitymentions):
						if entmen.sentid == sid:
							if entmen.start <= x and x < entmen.end:
								vsotup[2] = i
			if vsotup[1] != -1 or vsotup[2] != -1:
				self.verbsubobj.append(vsotup)


	# lexical features comprise of word2vec features for headword, lemma and depth of head word in dependency tree
	def gen_lexical_features(self, eobj):
		(word,lemma,pos) = self.wordfeatures[(eobj.sentid,eobj.head)]
		f1 = get_word2vec_feat(self.w2vmodel,word)
		f2 = get_word2vec_feat(self.w2vmodel,lemma)
		f3 = np.array([self.parsetrees[eobj.sentid].get_depth(eobj.head)])
		return np.concatenate((f1,f2,f3), axis=0)

	
	# class features comprise of POS feature vector of head word and WORD-CLASS feature vector of head word
	def gen_class_features(self, eobj):
		postag = self.wordfeatures[(eobj.sentid, eobj.head)][2]
		pos_feat = get_pos_feat(postag)
		class_feat = get_class_feat(postag)
		return np.concatenate((pos_feat, class_feat), axis = 0)

	# wordnet feature comprise only of the lexicographic synset based features 
	def gen_wordnet_features(self, eobj):
		word = self.wordfeatures[(eobj.sentid, eobj.head)][0]
		return np.array(get_wordnet_feat(word))
	
	# context features consist of 2 things:
	#	1. word2vec features of 2 words left to the head word and of 2 words to the right of head word
	#	2  POS features of 2 words left to the head word and of 2 words to the right of head word
	def gen_context_features(self, eobj):
		sentid = eobj.sentid
		tokenid = eobj.head
		N = 2
		wveclist = np.array([])	
		poslst = []
		maxtokens = self.numtokens[sentid - 1]
		for i in range(tokenid - N, tokenid)+range(tokenid + 1, tokenid + 1 + N):
			if i < 1 or i > maxtokens:
				posi = get_pos_feat('')
				wveclist = np.concatenate((wveclist,get_word2vec_feat(self.w2vmodel,'')),axis=0)
			else:
				posi = get_pos_feat(self.wordfeatures[(sentid, i)][2])
				wveclist = np.concatenate((wveclist,get_word2vec_feat(self.w2vmodel,self.wordfeatures[(sentid, i)][1])),axis=0)
			poslst += posi
		return np.concatenate((np.array(poslst),wveclist),axis=0)


	def gen_dependency_features(self,eobj):
		depgraph = self.dependgraphs[eobj.sentid][0]
		deplabels = self.dependgraphs[eobj.sentid][1]
		hwid = eobj.head
		deprellabel = ''
		dephw = ''
		deppos = ''
		for x in depgraph.GetNI(hwid).GetInEdges():
			deprellabel = deplabels[(x,hwid)]
			if x != 0:	#In case x depends on root, then word features are not defined
				dephw = self.wordfeatures[(eobj.sentid,x)][1]
				deppos = self.wordfeatures[(eobj.sentid,x)][2]
			break
		#return(deprellabel,dephw,deppos)
		f1_deplabel = np.array(get_dependency_rellabel(deprellabel))
		f2_dephw = 	get_word2vec_feat(self.w2vmodel,dephw)
		f3_deppos = np.array(get_pos_feat(deppos))
		return np.concatenate((f1_deplabel, f2_dephw, f3_deppos), axis = 0)


	def get_entity_mention_features(self):
		self.entityfeatures = []
		for entmen in self.entitymentions:
			a = self.gen_lexical_features(entmen)
			b = self.gen_class_features(entmen)
			c = self.gen_wordnet_features(entmen)
			d = self.gen_context_features(entmen)
			e = self.gen_dependency_features(entmen)
			ans = np.concatenate((a,b,c,d,e), axis = 0)
			self.entityfeatures.append(ans)


	def get_event_mention_features(self):
		self.eventfeatures = []
		for evemen in self.eventmentions:
			a = self.gen_lexical_features(evemen)
			b = self.gen_class_features(evemen)
			c = self.gen_wordnet_features(evemen)
			d = self.gen_context_features(evemen)
			e = self.gen_dependency_features(evemen)
			ans = np.concatenate((a,b,c,d,e), axis = 0)
			self.eventfeatures.append(ans)


########################################			

'''def main():
	fname = sys.argv[1]
	obj = docStructure(fname)
	obj.get_event_mentions()
	obj.get_entity_mentions()
	obj.get_entity_mention_features()
	obj.get_event_mention_features()

if __name__ == "__main__":
	main()
'''
