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

	
	def paradistance(self, vec1, vec2, metric):
		temp = vec1 - vec2
		return np.dot(temp , metric * temp)
	

	def update_entity_labels(self):
		shuffkeys =  self.hmentityfeat.keys()
		np.random.shuffle(shuffkeys)
		
		for entkey in shuffkeys:
			distances = np.zeros(self.kentity)
			
			# now retaining the required parts of self.lcorefcons and self.lcurentitycons
			req_corefcons = []
			req_curentitycons = []
			for tup in self.lcorefcons:
				if tup[0] == entkey:
					req_corefcons.append(tup)
				elif tup[1] == entkey:
					req_corefcons.append((tup[1], tup[0]))
			for tup in self.lcurentitycons:
				if tup[0] == entkey:
					req_curentitycons.append(tup)
				elif tup[1] == entkey:
					req_curentitycons.append((tup[1], tup[0]))

			# now looping over all the entity clusters and getting the distances
			for i in range(self.kentity):
				distances[i] += self.paradistance(self.hmentityfeat[entkey], self.hmentityclustcent[i], self.entitymetric)
				
				#now looking at the coref constraints
				for corefcon in req_corefcons:
					if self.hmentitylab[corefcon[1]] != i:
						distances[i] += self.wlarge * self.paradistance(self.hmentitfeat[entkey], self.hmentityfeat[corefcon[1]], self.entitymetric)
				#now looking at the current entity constraints
				for curentcon in req_curentitycons:
					if self.hmentitylab[curentcon[1]] != i:
						distances[i] += self.wsmall * self.paradistance(self.hmentityfeat[entkey], self.hmentityfeat[curentcon[1]], self.entitymetric)
			# now deciding the label
			reqdlabel = np.argmin(distances)
			self.hmentitylab[entkey] = reqdlabel


	def update_event_labels(self):
		shuffkeys = self.hmeventfeat.keys()
		np.random.shuffle(shuffkeys)
		
		for evtkey in shuffkeys:
			distances = np.zeros(self.kevent)
			
			#now we only need self.lcureventcons
			req_cureventcons= []
			for curevtcon in self.lcureventcons:
				if curevtcon[0] == evtkey:
					req_cureventcons.append(curevtcon)
				elif curevtcon[1] == evtkey:
					req_cureventcons.append((curevtcon[1], curevtcon[0]))
				
			## now we look at distances from the kevent clusters
			for i in range(self.kevent):
				distances[i] += self.paradistance(self.hmeventfeat[evtkey], self.hmeventclustercent[i], self.eventmetric)
			
				## now looking at thhe current event constraints		
				for curevtcon in req_cureventcons:
					if self.hmeventlab[curevtcon[1]] != i:
						distances[i] += self.wtiny * self.paradistance(self.hmeventfeat[evtkey], self.hmeventfeat[curevtcon[1]], self.eventmetric)
			
			reqlabel = np.argmin(distances)
			self.hmeventlab[evtkey] = reqlabel


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
					self.lcurentitycons.append((tempv[1][j],tempv[1][k]))


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


	def update_entity_metric(self,):
		pass



	def update_event_metric(self,):
		pass	


	def update_event_clustercents(self,):
		pass


	def update_entity_clustercents(self,):
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
