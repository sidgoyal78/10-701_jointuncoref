from store_objects import storeClass
import dill

####################

def extract_labels_for_scoring(menfname,scobjfname,opfname,option):
	'''option indicates whether you want to score entity, event or joint coreference
	0 - entity coreference, 1 - event coreference, 2 - joint corefernce'''

	scobjfptr = open(scobjfname,'rb')
	scobjlist = dill.load(scobjfptr)
	scobjfptr.close()
	hmdocidtoscobj = {}	#Integer keys
	for scobj in scobjlist:
		docid = int(scobj.filename.split('/')[-1].split('_')[2].split('.')[0])	#REMOVE .split('/')
		hmdocidtoscobj[docid] = scobj
		for k,v in scobj.wordfeatures.iteritems():
			v.append([])	#List stores 3-tuples (coref_id,start_token_id,end_token_id)
	#Extract topic id from filename used while constructing storeClass object
	topid = scobjlist[0].filename.split('/')[-1].split('_')[1]	#REMOVE .split('/')	
	del(scobjlist)

	#Open the mention file and move the read head to the relevant part
	menfptr = open(menfname,'r')
	line = menfptr.readline()
	while not(line[line.index('\t') + 1:].startswith(topid)):
		line = menfptr.readline()

	while line[line.index('\t') + 1:].startswith(topid):
		#Remember that endtokind  is exclusive, correct for indexing starting from 0 for sentences and tokens
		(norv,_,docid,sentind,corefid,starttokind,endtokind,_,_) = line.split('\t')
		docid = int(docid)
		sentind = int(sentind) + 1
		if corefid[-1] == '*':
			corefid = corefid[:-1]
		corefid = int(corefid)
		starttokind = int(starttokind) + 1
		endtokind = int(endtokind) + 1
		if (option == 0 and norv == 'N') or (option == 1 and norv == 'V') or (option == 2):
			reldoc = hmdocidtoscobj[docid]
			for i in range(starttokind,endtokind):
				print line
				if ((sentind,i) in reldoc.wordfeatures) and ((sentind,starttokind) in reldoc.wordfeatures) and ((sentind,endtokind) in reldoc.wordfeatures):
					reldoc.wordfeatures[(sentind,i)][3].append((corefid,starttokind,endtokind))
		line = menfptr.readline()
	menfptr.close()

	opfptr = open(opfname,'w')
	#Add required header to output file
	opfptr.write('#begin document (topic' + str(topid) + ');\n')

	for docid in sorted(hmdocidtoscobj.keys()):
		reldoc = hmdocidtoscobj[docid]
		for (sentind,tokind) in sorted(reldoc.wordfeatures.keys()):
			#sentind-1, tokind-1 should be written as 0-indexing is required in output file
			onestr = 'doc' + str(docid) + '\t' + str(sentind-1) + '\t' + str(tokind-1) + '\t' + reldoc.wordfeatures[(sentind,tokind)][0] + '\t'
			startsends = []
			onlystarts = []
			onlyends = []
			for (corefid,starttokind,endtokind) in reldoc.wordfeatures[(sentind,tokind)][3]:
				startshere = (tokind == starttokind)
				endshere = (tokind + 1 == endtokind)
				if startshere and endshere:
					startsends.append(corefid)
				elif startshere:
					onlystarts.append((starttokind,corefid))
				elif endshere:
					onlyends.append((endtokind,corefid))
			lastcol = ''
			for x in startsends:
				lastcol += '(' + str(x) + ')|'
			for stok,cid in sorted(onlyends,reverse=True):
				lastcol += str(cid) + ')|'
			for etok,cid in sorted(onlystarts,reverse=True):
				lastcol += '(' + str(cid) + '|'
			if lastcol == '':
				lastcol = '-'
			elif lastcol[-1] == '|':
				lastcol = lastcol[:-1]
			onestr += lastcol + '\n'
			opfptr.write(onestr)
		opfptr.write('\n')
	#Add required footer to output file
	opfptr.write('#end document')
	opfptr.close()

####################

if __name__ == '__main__':
	menfname = 'mentions.txt'	#Information for all topics present in one file
	scobjfname = 'topic1_DS_ordered.pkl'	#This is topic specific
	opfname = 'entity_only_1.txt'
	option = 0
	extract_labels_for_scoring(menfname,scobjfname,opfname,option)


