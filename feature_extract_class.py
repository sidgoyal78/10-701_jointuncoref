from xml.dom import minidom
import sys
import snap
import sexpdata
from construct_parse_tree import Node, ParseTree
import numpy as np
from nltk.corpus import wordnet as wn
from collections import OrderedDict as OD

from feat_wordnet_pos_class import get_wordnet_feat, get_pos_feat, get_class_feat, get_dependency_rellabel  # for the wordnet, POS, class, dependency relation features

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
	parsetrees = None	#change will happen
	dependgraphs = None
	entitymentions = None
	entitycoref = None
	eventmentions = None	#change will happen here

	eventfeatures = None
	entityfeatures = None	
	
	def __init__(self, fname):
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

			#Shit will change here
			parstr = sent.getElementsByTagName('parse')[0].firstChild.data
			partreeobj = ParseTree(parstr, self.numtokens[-1])
			self.parsetrees[sentenceid] = partreeobj  # for getting the depth call partreeobj.get_depth(<tokenid>)


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
						
						#### NOW CALL GRAPH FUNCTION TO GET HEAD WORD ID
						head = self.gen_event_mention_head(sentid,start,end)
						txt = " ".join(tempwlist)
						self.eventmentions.append(eventMention(txt,sentid,start,end,head))	
						flag = False

			if flag == True:
				end = ntok + 1
				#### NOW CALL GRAPH FUNCTION TO GET HEAD WORD ID
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



	# lexical features comprise of word2vec features for headword, lemma and depth of head word in dependency tree
	def gen_lexical_features(self, eobj):
		depth_parsetree = self.parsetrees[eobj.sentid].get_depth(eobj.head)
		return np.array([depth_parsetree])  ### TO ALSO INCLUDE WORD2VEC features	
	
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
		# doing only the POS as of now, 
		## Note: HAVE TO INCLUDE WORD2VEC 
		
		lst = []
		maxtokens = self.numtokens[sentid - 1]
		for i in range(tokenid - N, tokenid)+range(tokenid + 1, tokenid + 1 + N):
			if i < 1 or i > maxtokens:
				ans = get_pos_feat('')
			else:
				ans = get_pos_feat(self.wordfeatures[(sentid, i)][2])
			lst += ans

		return np.array(lst)
			

	def get_entity_mention_features(self):
		self.entityfeatures = []
		for entmen in self.entitymentions:
			a = self.gen_lexical_features(entmen)
			b = self.gen_class_features(entmen)
			c = self.gen_wordnet_features(entmen)
			d = self.gen_context_features(entmen)
			e = self.gen_dependency_features(entmen)
#			print "lexical    ", a
#			print "class      ", b
#			print "wordnet    ", c
#			print "context    ", d
#			print "dependency    ", e
#			print	
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
		f1_deplabel = get_dependency_rellabel(deprellabel)
		f2_dephw = [] # USE WORD2VEC	
		f3_deppos = get_pos_feat(deppos)
		return np.concatenate((f1_deplabel, f2_dephw, f3_deppos), axis = 0)

########################################			

def main():
	fname = sys.argv[1]
	obj = docStructure(fname)
	obj.get_event_mentions()
	obj.get_entity_mentions()
	obj.get_entity_mention_features()
	obj.get_event_mention_features()

if __name__ == "__main__":
	main()
