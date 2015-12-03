#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import sexpdata
import sys, codecs

class Node:
	def __init__(self, attr):
		self.data = attr
		self.ptr = []
		self.numch = 0

class ParseTree:
	
	def __init__(self, parstr, numtokens):
		self.hm = {}
		self.flag = 0
		parstr = parstr.replace(u'\xa0', u'-')
##		print parstr
#		print numtokens
#		print
		sexpl = self.get_new_output(parstr, numtokens)
		self.parsetree = self.constructtree(sexpl)
		self.numtokens = numtokens
		self.parselevellists = []
		self.levelorder()
	
	def get_depth(self, tokenid):
		## for the first level, depth is assumed to be 0
		if tokenid > self.numtokens or tokenid <= 0:
			return -1
		key = unicode(tokenid)
		for i in range(len(self.parselevellists)):
			if key in self.parselevellists[i]:
				return i
		return -1
			
		
        def get_new_output(self, string, ntok):
		ptr = 1
		a = string.split()
		finalstring = ''	
		for i in a:
			
			fl1 = i.find('(')
			if fl1 != -1:
				#then there it has to be a tag
				finalstring += i[0] + '"' + i[1:] + '" '
			else:
				#there has to be an ending tag, which means there has to be a token
				fl1 = i.find(')')
				self.hm[ptr] = i[:fl1]
				finalstring += '"' +  unicode(ptr) + '"' + i[fl1:] + ' '
				ptr += 1
		return sexpdata.loads(finalstring)	
			

	def constructtree(self, strlist):
#		if self.flag == 0:
#			self.flag = 1
#			print
#			print
#			print "Called with", strlist
#			print
#		print "--strlist--", strlist
		if len(strlist) == 0:
			return None

		root = Node(strlist[0])
		if len(strlist) == 2 and type(strlist[1]) == unicode:
			root.numch = 1
			root.ptr.append(Node(strlist[1]))
			return root
	
		root.numch = len(strlist) - 1
		for i in range(1, len(strlist)):
			root.ptr.append(self.constructtree(strlist[i]))
		
		return root

	def levelorder(self):
		if self.parsetree == None:
			return
		q1 = []
		q2 = []
		q1.append(self.parsetree)
		while(1):
			templist = []
			while(len(q1) != 0):
				val = q1.pop(0)
				templist.append(val.data)
				for i in range(val.numch):
					q2.append(val.ptr[i])

		    	self.parselevellists.append(templist)
			q1 = q2[:]
		   	q2 = []
		    	if (len(q1) == 0):
				break



'''strn = ['NP', ['NP', ['NP', ['DT', 'Another'], ['NN', 'day']], ['PP', ['IN', 'in'], ['NP', ['NNP', 'Hollywood']]]], [':', ';'], ['NP', ['NP', ['DT', 'another'], ['NN', 'star']], ['PP', ['IN', 'in'], ['NP', ['NN', 'rehab']]]], ['.', '.']]

strn = ['ROOT', ['NP', ['NP', ['NP', ['DT', 'Another'], ['NN', 'day']], ['PP', ['IN', 'in'], ['NP', ['NNP', 'Hollywood']]]], [':', ';'], ['NP', ['NP', ['DT', 'another'], ['NN', 'star']], ['PP', ['IN', 'in'], ['NP', ['NN', 'rehab']]]], ['.', '.']]]

mv = u'(ROOT (NP (NP (NP (DT Another) (NN day)) (PP (IN in) (NP (NNP Hollywood)))) (: ;) (NP (NP (DT another) (NN star)) (PP (IN in) (NP (NN rehab)))) (. .)))'

tkl = [u'Another', u'day', u'in', u'Hollywood', u';', u'another', u'star' , u'in', u'rehab', u'.']
obj = ParseTree(mv, tkl)
print obj.parselevellists
for i in range(1, 11):
	print obj.get_depth(i)'''
