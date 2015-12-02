import dill
import numpy as np


class PCKMeans:
	#Variable Initializations
	kentity = None	#Ideas - assume average cluster size, regression model
	kevent = None	#Ideas - assume average cluster size, regressino model
	wlarge = None
	wsmall = None
	wtiny = None
	numiter = None	#Could replace with convergence based stopping later

	entityfeaturedim = None
	eventfeaturedim = None
	entitymetric = None
	eventmetric = None

	hmentityfeat = None
	hmeventfeat = None
	lcorefcons = None
	lallvso = None

	hmentitylab = None
	hmeventlab = None
	hmentityclustcent = None
	hmeventclustcent = None

	lcurentitycons = None
	lcureventcons = None


	def __init__(self,fpath,kentity,kevent,wlarge,wsmall,wtiny,numiter):
		self.kentity = kentity
		self.kevent = kevent
		self.wlarge = wlarge
		self.wsmall = wsmall
		self.wtiny = wtiny
		self.numiter = numiter

		self.hmentityfeat = {}
		self.hmeventfeat = {}
		self.lcorefcons = []
		self.lallvso = []
		alldocobjs = dill.load(open(fpath,'rb'))

		self.entityfeaturedim = len(alldocobjs[0].entityfeatures[0]) 
		self.eventfeaturedim = len(alldocobjs[0].eventfeatures[0])
		self.entitymetric = np.ones(self.entityfeaturedim)
		self.eventmetric = np.ones(self.eventfeaturedim)

		for (i,docobj) in enumerate(alldocobjs):
			#document index is i
			for (j,entfeat) in enumerate(docobj.entityfeatures):
				self.hmentityfeat[(i,j)] = entfeat
			for (j,evtfeat) in enumerate(docobj.eventfeatures):
				self.hmeventfeat[(i,j)] = evtfeat
			for coreflist in docobj.entitycoref:
				for j in range(len(coreflist)):
					for k in range(j+1,len(coreflist)):
						self.lcorefcons.append(((i,coreflist[j]),(i,coreflist[k])))
			for vsol in docobj.verbsubobj:
				self.lallvso.append(((i,vsol[0]),(i,vsol[1]),(i,vsol[2])))
		#Unconstrained k-means for initalization of cluster labels and centroids for entity and event mentions
		self.initial_kmeans()
		self.construct_entitycons_from_eventclust()
		self.start_iterations()


	def start_iterations(self,):
		for i in range(self.numiter):
			self.update_entity_labels()
			self.update_entity_clustercents()
			self.update_entity_metric()
			self.construct_eventcons_from_entityclust()
			self.update_event_labels()
			self.update_event_clustercents()
			self.update_event_metric()
			self.construct_entitycons_from_eventclust()
			self.compute_objective_function()


	def construct_entitycons_from_eventclust(self):
		#store pairwise constraints as tuples in a list: lcurentitycons
		self.lcurentitycons = []
		hmtempeventcons = {}
		for i in range(kevent):
			hmtempeventcons[i] = ([],[])
		for v,s,o  in lallvso:
			tempkey = hmeventlab[v]
			if s[1] != -1:
				hmtempeventcons[tempkey][0].append(s)
			if o[1] != -1:
				hmtempeventcons[tempkey][1].append(o)
		for tempk, tempv in hmtempeventcons.iteritems():
			#self.lcurentitycons.append()
			for j in range(len(tempv[0])):
				for k in range(j+1,len(tempv[0])):
					self.lcurentitycons.append((tempv[0][j],tempv[0][k]))
			for j in range(len(tempv[1])):
				for k in range(j+1,len(tempv[1])):
					self.lcurentitymentions.append((tempv[1][j],tempv[1][k]))


	def construct_eventcons_from_entityclust(self):
		#store pairwise constraints as tuples in a list: lcureventcons
		self.lcureventcons = []
		hmtempentitycons = {}
		for i in range(kentity):
			hmtempentitycons[i] = ([],[])
		for v,s,o in lallvso:
			if s[1] != -1:
				stempkey = hmentitylab[s]
				hmtempentitycons[stempkey][0].append(v)
			if o[1] != -1:
				otempkey = hmentitylab[o]
				hmtempentitycons[otempkey][1].append(v)
		for tempk, tempv in hmtempentitycons.iteritems():
			#self.lcureventcons.append()
			for j in range(len(tempv[0])):
				for k in range(j+1,len(tempv[0])):
					self.lcureventcons.append((tempv[0][j],tempv[0][k]))
			for j in range(len(tempv[1])):
				for k in range(j+1,len(tempv[1])):
					self.lcureventcons.append((tempv[1][j],tempv[1][k]))


	def compute_objective_function(self,):
		pass


	def update_entity_labels(self,):
		pass


	def update_entity_clustercents(self,):
		pass


	def update_entity_metric(self,):
		pass


	def update_event_labels(self,):
		pass


	def update_event_clustercents(self,):
		pass


	def update_event_metric(self,):
		pass	


	def initial_kmeans(self,):
		pass




#####FOR TESTING PURPOSES ONLY#####

if __name__ == '__main__':
	fpath = 'topic1_DS_objects.pkl'
	kentity = 10
	kevent = 10
	wlarge = 8
	wsmall = 4
	wtiny = 1
	numiter = 10
	shitobj = PCKMeans(fpath,kentity,kevent,wlarge,wsmall,wtiny,numiter)
	#print len(shitobj.hmentityfeat.keys()), len(shitobj.hmeventfeat.keys())
	#print sorted(shitobj.hmentityfeat.keys())
	#print sorted(shitobj.hmeventfeat.keys())
	#print shitobj.hmentityfeat[(14,0)]
	#print shitobj.hmentityfeat[(14,0)].shape
