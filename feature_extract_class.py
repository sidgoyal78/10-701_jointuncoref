from xml.dom import minidom
import sys

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
	pass

########################################

class docStructure:
	
	def __init__(self, fname):
		self.xmldoc = minidom.parse(fname)
		itemlist = self.xmldoc.getElementsByTagName('sentences')

		self.wordfeatures = {}
		for i in itemlist:
			## "inside sentences"
			sentencelist = i.getElementsByTagName('sentence')
			for sent in sentencelist:
				sentenceid = sent.getAttribute('id')
				tokenlist = sent.getElementsByTagName('token')			
				for tok in tokenlist:
					tokenid = tok.getAttribute('id')	
					word = tok.getElementsByTagName('word')[0] #only one word is present per token	
					lemma = tok.getElementsByTagName('lemma')[0] #only one word is present per token	
					pos = tok.getElementsByTagName('POS')[0] #only one word is present per token	
					self.wordfeatures[(sentenceid, tokenid)] = [word.firstChild.data, lemma.firstChild.data, pos.firstChild.data]
		print self.wordfeatures


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
				txt = m.getElementsByTagName("text")[0].firstChild.data
				sentid = m.getElementsByTagName("sentence")[0].firstChild.data
				start = m.getElementsByTagName("start")[0].firstChild.data
				end = m.getElementsByTagName("end")[0].firstChild.data
				head = m.getElementsByTagName("head")[0].firstChild.data	
				corefcons.append(len(self.entitymentions))
				self.entitymentions.append(entityMention(txt,sentid,start,end,head))
			self.entitycoref.append(corefcons)


'''		itemlist = self.xmldoc.getElementsByTagName('mention')
		self.entitylist = []
		for i in itemlist:
			txt = i.getElementsByTagName("text")[0].firstChild.data
			sentid = i.getElementsByTagName("sentence")[0].firstChild.data
			start = i.getElementsByTagName("start")[0].firstChild.data
			end = i.getElementsByTagName("end")[0].firstChild.data
			head = i.getElementsByTagName("head")[0].firstChild.data
			self.entitylist.append(entityObj(txt, sentid, start, end, head))
			print txt, sentid, start, end, head

		print self.entitylist'''


	def get_event_mentions():
		pass


'''	def gen_entity_mention_features():
		pass


	def gen_event_mention_features():
		pass'''

########################################			

def main():
	fname = sys.argv[1]
	obj = docStructure(fname)
	obj.get_entity_mentions()

if __name__ == "__main__":
	main()
