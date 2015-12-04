from pckmeans_with_writer  import *

#####FOR TESTING PURPOSES ONLY#####

def makemetricplot(met):
	d = met.reshape(44,55)
	c = np.ma.masked_where(d <= 0.5, d, copy=False)
	plt.imshow(c, interpolation = 'nearest')
	plt.colorbar()
	plt.show()

def plotmultiple(mlst, k1, k2, topicid, output):
	for i in range(len(mlst)):
		plt.plot(mlst[i])
	plt.xlabel("Number of iteration")
	plt.ylabel("Objective function value")
	plt.title("Topic " + str(topicid) + ", kentity=" + str(k1) + ", kevent=" + str(k2))
	plt.savefig(output)

def main():
	topicid = 26
	fpath = '../topicobjects/topic' + str(topicid) +  '_DS_ordered.pkl'
	kentity = 20
	kevent = 10
	wlarge = 8
	wsmall = 4
	wtiny = 1
	numiter = 10


	ranruns = 5
	mlst = []
	opdir = 'jvsiter_plots/'
	opfname = opdir + "topic" + str(topicid) + "_kentity" + str(kentity) + "_kevent" + str(kevent)
	for i in range(ranruns):
		pckobj = PCKMeans(fpath,kentity,kevent,wlarge,wsmall,wtiny,numiter)
		mlst.append(pckobj.objfunctionvalues)
	plotmultiple(mlst, kentity, kevent, topicid, opfname)

	#entfile = 'topic1_onlyentity.txt'
	#evtfile = 'topic1_onlyevent.txt'
	#bothfile = 'topic1_both.txt'
	#pckobj.writelog(entfile, evtfile, bothfile)
	#print pckobj.entitymetric
	#print pckobj.eventmetric	
	#print len(pckobj.eventmetric)
#	makemetricplot(pckobj.entitymetric)
#	makemetricplot(pckobj.eventmetric)

	
if __name__ == "__main__":
	main()
