import sys

class Node:
	def __init__(self, attr):
		self.data = attr
		self.ptr = []
		self.numch = 0

class ParseTree:
	
	def constructtree(self, strlist):
		if len(strlist) == 0:
			return None

		root = Node(strlist[0])
		if len(strlist) == 2 and type(strlist[1]) == str:
			root.numch = 1
			root.ptr.append(Node(strlist[1]))
			return root
	
		root.numch = len(strlist) - 1
		for i in range(1, len(strlist)):
			root.ptr.append(self.constructtree(strlist[i]))
		
		return root

	def levelorder(self, root):
		if root == None:
			return
		
		q1 = []
		q2 = []
		q1.append(root)
		while(1):

		    while(len(q1) != 0):
			val = q1.pop(0)
			print val.data,
			for i in range(val.numch):

				q2.append(val.ptr[i])
		    print	
		    q1 = q2[:]
		    q2 = []
		    if (len(q1) == 0):
			    break

			

strn = ['NP', ['NP', ['NP', ['DT', 'Another'], ['NN', 'day']], ['PP', ['IN', 'in'], ['NP', ['NNP', 'Hollywood']]]], [':', ';'], ['NP', ['NP', ['DT', 'another'], ['NN', 'star']], ['PP', ['IN', 'in'], ['NP', ['NN', 'rehab']]]], ['.', '.']]

strn = ['ROOT', ['NP', ['NP', ['NP', ['DT', 'Another'], ['NN', 'day']], ['PP', ['IN', 'in'], ['NP', ['NNP', 'Hollywood']]]], [':', ';'], ['NP', ['NP', ['DT', 'another'], ['NN', 'star']], ['PP', ['IN', 'in'], ['NP', ['NN', 'rehab']]]], ['.', '.']]]

val = ParseTree()
rt = val.constructtree(strn)
print val.levelorder(rt)
