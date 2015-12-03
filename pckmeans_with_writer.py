import dill
import numpy as np
import sklearn.cluster as sc
import matplotlib.pyplot as plt
import copy

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
	metricupdateshift = 0.00001

	objfunctionvalues = None

	def __init__(self,fpath,kentity,kevent,wlarge,wsmall,wtiny,numiter):
		self.kentity = kentity
		self.kevent = kevent
		self.wlarge = wlarge
		self.wsmall = wsmall
		self.wtiny = wtiny
		self.numiter = numiter

		self.objfunctionvalues = []

		self.hmentityfeat = {}
		self.hmeventfeat = {}
		self.lcorefcons = []
		self.lallvso = []
		alldocobjs = dill.load(open(fpath,'rb'))
		
		## added one more member	
		self.dlobj = alldocobjs

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
			f = self.compute_objective_function()
			print f
			self.objfunctionvalues.append(f)
			
	
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
						distances[i] += self.wlarge * self.paradistance(self.hmentityfeat[entkey], self.hmentityfeat[corefcon[1]], self.entitymetric)
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
				distances[i] += self.paradistance(self.hmeventfeat[evtkey], self.hmeventclustcent[i], self.eventmetric)
			
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
		for i in range(self.kevent):
			hmtempeventcons[i] = ([],[])
		for v,s,o  in self.lallvso:
			tempkey = self.hmeventlab[v]
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
		for i in range(self.kentity):
			hmtempentitycons[i] = ([],[])
		for v,s,o in self.lallvso:
			if s[1] != -1:
				stempkey = self.hmentitylab[s]
				hmtempentitycons[stempkey][0].append(v)
			if o[1] != -1:
				otempkey = self.hmentitylab[o]
				hmtempentitycons[otempkey][1].append(v)
		for tempk, tempv in hmtempentitycons.iteritems():
			#self.lcureventcons.append()
			for j in range(len(tempv[0])):
				for k in range(j+1,len(tempv[0])):
					self.lcureventcons.append((tempv[0][j],tempv[0][k]))
			for j in range(len(tempv[1])):
				for k in range(j+1,len(tempv[1])):
					self.lcureventcons.append((tempv[1][j],tempv[1][k]))


	def update_entity_clustercents(self):
		runcount = {}
		for i in range(self.kentity):
			self.hmentityclustcent[i] = np.zeros(self.entityfeaturedim)
			runcount[i] = 0
		for ent,feat in self.hmentityfeat.iteritems():
			k = self.hmentitylab[ent]
			runcount[k] += 1
			self.hmentityclustcent[k] += feat
		for i in range(self.kentity):
			if runcount[i] != 0:
				self.hmentityclustcent[i] /= runcount[i]


	def update_event_clustercents(self):
		runcount = {}
		for i in range(self.kevent):
			self.hmeventclustcent[i] = np.zeros(self.eventfeaturedim)
			runcount[i] = 0
		for eve,feat in self.hmeventfeat.iteritems():
			k = self.hmeventlab[eve]
			runcount[k] += 1
			self.hmeventclustcent[k] += feat
		for i in range(self.kevent):
			if runcount[i] != 0:
				self.hmeventclustcent[i] /= runcount[i]


	def update_entity_metric(self):
		self.entitymetric = np.ones(self.entityfeaturedim) * self.metricupdateshift
		nummentions = len(self.hmentityfeat)
		for ent,feat in self.hmentityfeat.iteritems():
			k = self.hmentitylab[ent]
			self.entitymetric += (feat - self.hmentityclustcent[k]) ** 2
		for ent1, ent2 in self.lcorefcons:
			k1 = self.hmentitylab[ent1]
			k2 = self.hmentitylab[ent2]
			if k1 != k2:
				self.entitymetric += self.wlarge * (self.hmentityfeat[ent1] - self.hmentityfeat[ent2])**2
		for ent1, ent2 in self.lcurentitycons:
			k1 = self.hmentitylab[ent1]
			k2 = self.hmentitylab[ent2]
			if k1 != k2:
				self.entitymetric += self.wsmall * (self.hmentityfeat[ent1] - self.hmentityfeat[ent2])**2
		self.entitymetric = float(nummentions)/self.entitymetric


	def update_event_metric(self,):
		self.eventmetric = np.ones(self.eventfeaturedim) * self.metricupdateshift
		nummentions = len(self.hmeventfeat)
		for eve, feat in self.hmeventfeat.iteritems():
			k = self.hmeventlab[eve]
			self.eventmetric += (feat - self.hmeventclustcent[k]) ** 2
		for eve1, eve2 in self.lcureventcons:
			k1 = self.hmeventlab[eve1]
			k2 = self.hmeventlab[eve2]
			if k1 != k2:
				self.eventmetric += self.wtiny * (self.hmeventfeat[eve1] - self.hmeventfeat[eve2]) ** 2
		self.eventmetric = float(nummentions)/self.eventmetric


	def initial_kmeans(self):
		self.hmentitylab = {}
		self.hmeventlab = {}
		self.hmentityclustcent = {}
		self.hmeventclustcent = {}
	
		obj = sc.KMeans(init = 'k-means++', n_clusters = self.kentity)
		tempentlist = []
		hmtempent = {}
		#populate the temporary hashmap
		for ent, feat in self.hmentityfeat.iteritems():
			tempentlist.append(feat)
			hmtempent[ent] = len(tempentlist) - 1
			
		obj.fit(tempentlist)
		labels = obj.predict(tempentlist)
		for ent in hmtempent:
			index = hmtempent[ent]	
			curlab = labels[index]
			self.hmentitylab[ent] = curlab
		
		for i in range(len(obj.cluster_centers_)):
			self.hmentityclustcent[i] = obj.cluster_centers_[i]

		## now doing the same for events
		objevt = sc.KMeans(init = 'k-means++', n_clusters =  self.kevent)
		tempevtlist = []
		hmtempevt = {}
		for evt, feat in self.hmeventfeat.iteritems():
			tempevtlist.append(feat)
			hmtempevt[evt] = len(tempevtlist) - 1
		
		objevt.fit(tempevtlist)
		labels = objevt.predict(tempevtlist)	
		for evt in hmtempevt:
			index = hmtempevt[evt]
			curlab = labels[index]
			self.hmeventlab[evt] = curlab
		for i in range(len(objevt.cluster_centers_)):
			self.hmeventclustcent[i] = objevt.cluster_centers_[i]
			

	def compute_objective_function(self):
		J = 0.0

		# Initially looking at terms concerning the entity mentions
		for ent, feat in self.hmentityfeat.iteritems():
			k = self.hmentitylab[ent]
			J += self.paradistance(feat, self.hmentityclustcent[k], self.entitymetric)

		tempsum = 0.0
		for i in self.entitymetric:
			tempsum += np.log(i)
		J -= tempsum
		
		#now looking at coref entity constraints
		for ent1, ent2 in self.lcorefcons:
			k1 = self.hmentitylab[ent1]
			k2 = self.hmentitylab[ent2]
			if k1 != k2:
				J += self.wlarge * self.paradistance(self.hmentityfeat[ent1], self.hmentityfeat[ent2], self.entitymetric)
		
		# now looking at current entity constraints
		for ent1, ent2 in self.lcurentitycons:
			k1 = self.hmentitylab[ent1]
			k2 = self.hmentitylab[ent2]
			if k1 != k2:
				J += self.wsmall * self.paradistance(self.hmentityfeat[ent1], self.hmentityfeat[ent2], self.entitymetric)
		
		## now, we consider the event constraints
		for evt, feat in self.hmeventfeat.iteritems():
			k = self.hmeventlab[evt]
			J += self.paradistance(feat, self.hmeventclustcent[k], self.eventmetric)

		tempsum = 0.0
		for i in self.eventmetric:
			tempsum += np.log(i)
		J -= tempsum
		
		# now looking at the current event constraints
		for evt1, evt2 in self.lcureventcons:
			k1 = self.hmeventlab[evt1]	
			k2 = self.hmeventlab[evt2]	
			if k1 != k2:
				J += self.wtiny * self.paradistance(self.hmeventfeat[evt1], self.hmeventfeat[evt2], self.eventmetric)
		
		return J

	def modifyparanthesis(self, listofid):

		for i in range(len(listofid)):
			sublist = listofid[i]

			flag  = 0
			if type(sublist[0]) == int:
				flag = 1
				toadd = "(" + str(sublist[0])
				if type(sublist[1]) != int or  sublist[1] != sublist[0]:
					flag = 0
					toadd  += ")"
				sublist[0] = toadd
			else:
				sublist[0] = '-'
			for i in range(1, len(sublist) - 1):
				if type(sublist[i]) == int:
					if  flag == 1:
						if type(sublist[i+1]) == int and sublist[i+1] == sublist[i]:
							sublist[i] = '-'
						else:
							sublist[i] = str(sublist[i]) + ")"
							flag = 0
					elif flag == 0:
						toadd = "(" + str(sublist[i])
						flag = 1
						if type(sublist[i+1]) != int or sublist[i + 1]!=sublist[i]:
							toadd += ")"
							flag = 0
						sublist[i] = toadd
				else:
					sublist[i] = '-'
			if flag == 1:
				sublist[-1] = str(sublist[-1]) + ")"
			else:
				sublist[-1] = '-'



	def writelog(self, fname1, fname2, fname3, fname4, topicid):

		f1 = open(fname1, 'w')
		f2 = open(fname2, 'w')
#		f3 = open(fname3, 'w')

		f4 = open(fname4, 'w')

		f1.write('## Entity(N) or Event(V)?' + '\t' + 'Topic' + '\t' + 'Doc' + '\t' + 'Sentence Number' +'\t' +  'CorefID' + '\t' + 'StartIdx'  +  '\t' + 'EndIdx' + '\t' +  'StartCharIdx' + '\t'    + 'EndCharIdx' + '\n')
		f2.write('## Entity(N) or Event(V)?' + '\t' + 'Topic' + '\t' + 'Doc' + '\t' + 'Sentence Number' +'\t' +  'CorefID' + '\t' + 'StartIdx'  +  '\t' + 'EndIdx' + '\t' +  'StartCharIdx' + '\t'    + 'EndCharIdx' + '\n')
		f4.write('## Entity(N) or Event(V)?' + '\t' + 'Topic' + '\t' + 'Doc' + '\t' + 'Sentence Number' +'\t' +  'CorefID' + '\t' + 'StartIdx'  +  '\t' + 'EndIdx' + '\t' +  'StartCharIdx' + '\t'    + 'EndCharIdx' + '\n')
		#f1.write('#begin document (topic'  + str(topicid) + 'entity);' + '\n')
		#f2.write('#begin document (topic' + str(topicid) + 'event);' + '\n')
		#f3.write('#begin document (topic' + str(topicid) + 'both);' + '\n')
	

		obcnt = 0
		for i in range(len(self.dlobj)):
			curobj = self.dlobj[i]  # the current object
			name, topic, docid = curobj.filename.split('/')[-1].split('.')[0].split('_')
			allsent = []
			allcorresp = []
			alleventmentions = []
			allentitymentions = []
			alltogether = []

			thmidx = {}  # hash map for special format in the joint entity and event setting
			hmonlyevt = {}
			hmonlyent = {}
			for j in range(curobj.numsentences):
			# creating a sentence
				sentcounter = j + 1
				numtokens = curobj.numtokens[j]
					
				sentence = []
				corres = []
				evment = []
				enment = []
				for k in range(numtokens):
					sentence.append(curobj.wordfeatures[(sentcounter, k + 1)][0])
					corres.append(None)
					evment.append(None)
					enment.append(None)
				allsent.append(sentence)
				allcorresp.append(corres)
				alleventmentions.append(evment)
				allentitymentions.append(enment)
			
			encount = 0
			for j in curobj.entitymentions:
				entmenobj = j
				sentref = entmenobj.sentid - 1
				
				actuallabel = int(self.hmentitylab[(obcnt, encount)])
				for k in range(entmenobj.start - 1, entmenobj.end - 1):
					allentitymentions[sentref][k] = actuallabel
				encount += 1
				if entmenobj.sentid not in hmonlyent:
					hmonlyent[entmenobj.sentid] = [('N', entmenobj.start, entmenobj.end, actuallabel)] #just need actuallabels no need to shift			 
				else:
					hmonlyent[entmenobj.sentid].append(('N', entmenobj.start, entmenobj.end, actuallabel))


				if entmenobj.sentid not in thmidx:
					thmidx[entmenobj.sentid] = [('N', entmenobj.start, entmenobj.end, actuallabel + self.kevent)]
				else:
					thmidx[entmenobj.sentid].append(('N', entmenobj.start, entmenobj.end, actuallabel + self.kevent))

			alltogether = copy.deepcopy(allentitymentions)
			evtcount = 0
			for j in curobj.eventmentions:
				evtmenobj = j
				sentref = evtmenobj.sentid - 1
				actuallabel = int(self.hmeventlab[(obcnt, evtcount)])
				shiftedref = self.kentity
				for k in range(evtmenobj.start - 1, evtmenobj.end - 1):
					alleventmentions[sentref][k] = actuallabel
					alltogether[sentref][k] = actuallabel + shiftedref
				evtcount += 1
				if evtmenobj.sentid not in hmonlyevt:
					hmonlyevt[evtmenobj.sentid] = [('V', evtmenobj.start, evtmenobj.end, actuallabel)]
				else:
					hmonlyevt[evtmenobj.sentid].append(('V', evtmenobj.start, evtmenobj.end, actuallabel))
					
	
				if evtmenobj.sentid not in thmidx:
					thmidx[evtmenobj.sentid] = [('V', evtmenobj.start, evtmenobj.end, actuallabel)]
				else:
					thmidx[evtmenobj.sentid].append(('V', evtmenobj.start, evtmenobj.end, actuallabel))

			obcnt += 1

			self.indexwrite(f1, topic, docid, hmonlyent)
			self.indexwrite(f2, topic, docid, hmonlyevt)
			self.indexwrite(f4, topic, docid, thmidx)
#			print allsent
####			print
#			print allentitymentions
#			print

			self.modifyparanthesis(allentitymentions)

#			print
#			print alleventmentions
#			print

			self.modifyparanthesis(alleventmentions)
			self.modifyparanthesis(alltogether)
			#self.perdocwrite(f1,"doc" + docid, allsent, allentitymentions)
			#self.perdocwrite(f2,"doc" + docid, allsent, alleventmentions)
			#self.perdocwrite(f3, "doc" + docid, allsent, alltogether)
		#f1.write('#end document')
		#f2.write('#end document')
		#f3.write('#end document')

		f1.write("\t")
		f2.write("\t")
		f4.write("\t")

		f1.close()
		f2.close()
		#f3.close()
		f4.close()


	def indexwrite(self, fptr, topic, docid, thmidx):
		for i in sorted(thmidx.keys()):
			sentnum = i - 1
			for iden, pstart, pend, clustlabel in thmidx[i]:
				fptr.write(iden + "\t" + topic + "\t" + docid + "\t" + str(sentnum) + "\t" + str(clustlabel) + "\t" + str(pstart - 1) + "\t" + str(pend - 1) + "\t" + "0" + "\t" + "0" + "\n")

	def perdocwrite(self,fptr, fname, allsent, allment):
		for i in range(len(allsent)):
			for j in range(len(allsent[i])):
				fptr.write(fname + "\t" + str(i) + "\t" + str(j) + "\t" + allsent[i][j] + "\t" + allment[i][j] + "\n")
		fptr.write("\n")

	
#####FOR TESTING PURPOSES ONLY#####

if __name__ == '__main__':
	fpath = 'topic1_DS_ordered.pkl'
	kentity = 40
	kevent = 25
	wlarge = 8
	wsmall = 4
	wtiny = 1
	numiter = 5
	shitobj = PCKMeans(fpath,kentity,kevent,wlarge,wsmall,wtiny,numiter)
	#plt.plot(shitobj.objfunctionvalues)	
	#plt.show()
	
	entfile = 'topic1_onlyentity.txt'
	evtfile = 'topic1_onlyevent.txt'
	bothfile = 'evaltopic1both.txt'
	idxfile_for_gen = 'topic1_both.txt'
	topicid = 1
	shitobj.writelog(entfile, evtfile, bothfile, idxfile_for_gen, topicid)
	#print shitobj.hmentitylab
	#print len(shitobj.hmentityfeat.keys()), len(shitobj.hmeventfeat.keys())
	#print sorted(shitobj.hmentityfeat.keys())
	#print sorted(shitobj.hmeventfeat.keys())
	#print shitobj.hmentityfeat[(14,0)]
	#print shitobj.hmentityfeat[(14,0)].shape
