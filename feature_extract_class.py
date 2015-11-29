from xml.dom import minidom
import sys
import snap
import sexpdata
from construct_parse_tree import Node, ParseTree

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


'''	def gen_entity_mention_features():
		pass


	def gen_event_mention_features():
		pass'''

	def gen_entity_mention_features(self):
		self.entityfeatures = []
		
		for ent in self.entitymentions:
			reqdlist = self.wordfeatures[(ent.sentid, ent.head)]
		
			pos_feat = get_pos_features(reqdlist[2])
			class_feat = get_class_features(reqdlist[2])
			wordnet_feat = get_lxvector_wordnet(reqdlist[0])
			depth_parsetree = self.parsetrees[ent.sentid].get_depth(ent.head)
		

########################################			

def main():
	fname = sys.argv[1]
	obj = docStructure(fname)
	obj.get_event_mentions()

if __name__ == "__main__":
	main()
