from xml.dom import minidom
import sys

class entityObj:
	def __init__(self, txt, sentid, start, end, head):
		self.txt = txt
		self.sentid = sentid
		self.start = start
		self.end = end
		self.head = head
		

class GetStructure:
	
	def __init__(self, fname):
		self.xmldoc = minidom.parse(fname)
		itemlist = self.xmldoc.getElementsByTagName('sentences')

		self.hmap = {}
		for i in itemlist:
			## "inside sentences"
			sents = i.getElementsByTagName('sentence')
			for s in sents:
				sentenceid = s.getAttribute('id')
				temp = s.getElementsByTagName('token')
			
				for k in temp:
					tokenid = k.getAttribute('id')	
					word = k.getElementsByTagName("word")[0] #only one word is present per token	
					lemma = k.getElementsByTagName("lemma")[0] #only one word is present per token	
					pos = k.getElementsByTagName("POS")[0] #only one word is present per token	

					self.hmap[(sentenceid, tokenid)] = [word.firstChild.data, lemma.firstChild.data, pos.firstChild.data]
					print word.firstChild.data
		print self.hmap
		

	def get_entity_mentions(self):
		itemlist = self.xmldoc.getElementsByTagName('mention')
		self.entitylist = []
		for i in itemlist:
			txt = i.getElementsByTagName("text")[0].firstChild.data
			sentid = i.getElementsByTagName("sentence")[0].firstChild.data
			start = i.getElementsByTagName("start")[0].firstChild.data
			end = i.getElementsByTagName("end")[0].firstChild.data
			head = i.getElementsByTagName("head")[0].firstChild.data
			self.entitylist.append(entityObj(txt, sentid, start, end, head))
			print txt, sentid, start, end, head

		print self.entitylist
		
			
	
#itemlist = xmldoc.getElementsByTagName('mention')
#print(help(itemlist[0]))
#print(itemlist[0].attributes['text'].value)
#for i in itemlist: 
#	nickname = i.getElementsByTagName("text")[0]
#	print nickname.firstChild.data

def main():
	fname = sys.argv[1]
	obj = GetStructure(fname)
	obj.get_entity_mentions()

if __name__ == "__main__":
	main()
