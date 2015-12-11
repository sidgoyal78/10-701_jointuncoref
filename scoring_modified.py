from pckmeans_with_writer import PCKMeans
from label_extractor import extract_labels_for_scoring
import subprocess
from scipy.io import savemat
import numpy as np

####################



def runscore(topid, kenlist, kevlist, wratiolist, cmd):
	lstscore1 = {}
	lstscore2 = {}
	lstscore3 = {}
	inpfname = '../topicobjects/topic' + str(topid) + '_DS_ordered.pkl'
	for ken in kenlist:
		for kev in kevlist:
			for (wtiny,wsmall,wlarge) in wratiolist:

				

				entonlyfinal = 'entity_only_output/final/fin_top' + str(topid) + '_ken' + str(ken) + \
				'_kev' + str(kev) + '_wt' + str(wtiny) +  '_ws' + str(wsmall) + '_wl' + str(wlarge) + '.txt'
				evtonlyfinal = 'event_only_output/final/fin_top' + str(topid) + '_ken' + str(ken) + \
				'_kev' + str(kev) + '_wt' + str(wtiny) +  '_ws' + str(wsmall) + '_wl' + str(wlarge) + '.txt'
				entandevtfinal = 'entity_and_event_output/final/fin_top' + str(topid) + '_ken' + str(ken) + \
				'_kev' + str(kev) + '_wt' + str(wtiny) +  '_ws' + str(wsmall) + '_wl' + str(wlarge) + '.txt'


				entonlygoldfile = 'entity_only_output/final/top' + str(topid) + '.txt'
				evtonlygoldfile = 'event_only_output/final/top' + str(topid) + '.txt'
				entandevtgoldfile = 'entity_and_event_output/final/top' + str(topid) + '.txt'
				
				batcmd1 = './scorer.pl ' + cmd +  ' ' + entonlygoldfile + ' ' +  entonlyfinal + '  | tail -2 | head -1 | tr -s " " | cut -d " " -f 11'
				batcmd2 = './scorer.pl ' + cmd +  ' ' + evtonlygoldfile + ' ' +  evtonlyfinal + '  | tail -2 | head -1 | tr -s " " | cut -d " " -f 11'
				batcmd3 =  './scorer.pl ' + cmd +  ' ' + entandevtgoldfile + ' ' +  entandevtfinal  + '  | tail -2 | head -1 | tr -s " " | cut -d " " -f 11'
				result1 = subprocess.check_output(batcmd1, shell = True)	
				lstscore1[(ken, kev, wtiny, wsmall, wlarge)] =  float(result1[:-2])
				result2 = subprocess.check_output(batcmd2, shell = True)	
				lstscore2[(ken, kev, wtiny, wsmall, wlarge)] =  float(result2[:-2])
				result3 = subprocess.check_output(batcmd3, shell = True)	
				lstscore3[(ken, kev, wtiny, wsmall, wlarge)] =  float(result3[:-2])
	
	#print lstscore1
	#print
	#print lstscore2
	#print
	#print lstscore3
	return (lstscore1, lstscore2, lstscore3)

def return_muc( kenlist, kevlist, a, b, c, d, ind, weight_tuple):
	w1 = weight_tuple[0]
	w2 = weight_tuple[1]
	w3 = weight_tuple[2]
#	str1 = "0," 
#	strlist = [str(i) for i in kenlist]
#	str1 = str1 + ",".join(strlist) + "\n"
#	fptr.write(str1)
	fnlst = []

	for i in kevlist:
#		str2 = str(i) + ","
		val = []
		for j in kenlist:
			val.append( round(a[ind][(j, i, w1, w2, w3)] , 2))
#		str2 = str2 + ",".join(val) + "\n"
#		fptr.write(str2)
		fnlst.append(val)
	return np.array(fnlst)

def return_bcub( kenlist, kevlist, a, b, c, d, ind, weight_tuple):
	w1 = weight_tuple[0]
	w2 = weight_tuple[1]
	w3 = weight_tuple[2]
#	str1 = "0," 
#	strlist = [str(i) for i in kenlist]
#	str1 = str1 + ",".join(strlist) + "\n"
#	fptr.write(str1)
	fnlst = []

	for i in kevlist:
#		str2 = str(i) + ","
		val = []
		for j in kenlist:
			val.append( round(b[ind][(j, i, w1, w2, w3)] , 2))
#		str2 = str2 + ",".join(val) + "\n"
		fnlst.append(val)
	return np.array(fnlst)

def return_ceafe( kenlist, kevlist, a, b, c, d, ind, weight_tuple):
	w1 = weight_tuple[0]
	w2 = weight_tuple[1]
	w3 = weight_tuple[2]
#	str1 = "0," 
#	strlist = [str(i) for i in kenlist]
#	str1 = str1 + ",".join(strlist) + "\n"
#	fptr.write(str1)
	fnlst  = []

	for i in kevlist:
#		str2 = str(i) + ","
		val = []
		for j in kenlist:
			val.append(round(c[ind][(j, i, w1, w2, w3)] , 2))
#		str2 = str2 + ",".join(val) + "\n"
		fnlst.append(val)
	return np.array(fnlst)

def return_blanc(kenlist, kevlist, a, b, c, d, ind, weight_tuple):
	w1 = weight_tuple[0]
	w2 = weight_tuple[1]
	w3 = weight_tuple[2]
#	str1 = "0," 
#	strlist = [str(i) for i in kenlist]
#	str1 = str1 + ",".join(strlist) + "\n"
#	fptr.write(str1)
	fnlst = []

	for i in kevlist:
#		str2 = str(i) + ","
		val = []
		for j in kenlist:
			val.append(str( round(d[ind][(j, i, w1, w2, w3)] , 2)))
#		str2 = str2 + ",".join(val) + "\n"
#		fptr.write(str2)	
		fnlst.append(val)
	return np.array(fnlst)

def main():
	kenlist =  range(5, 24,2) # [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52]
	kevlist =  range(3, 22,2)
	wratiolist = [(1,2,4), (1,4,8),(1,8,16)]	#3-tuple with (w_tiny,w_small,w_large)
	topid = 45
	a = runscore(topid, kenlist, kevlist, wratiolist, 'muc')
	b = runscore(topid, kenlist, kevlist, wratiolist, 'bcub')
	c = runscore(topid, kenlist, kevlist, wratiolist, 'ceafe')
	d = runscore(topid, kenlist, kevlist, wratiolist, 'blanc')

	print "got all the scores"	
	# first line
#	f1 = open(str(topid) + '_onlyent.csv', 'w')
#	f2 = open(str(topid) + '_onlyevt.csv', 'w')
#	f3 = open(str(topid) + '_both.csv', 'w')

	arr1 = []
	namelst = ['muc', 'bcub', 'ceafe', 'blanc']
	for i in range(len(wratiolist)):
		temp = []
		for j in range(len(namelst)):
			temp.append(namelst[j] + "_w" + str(i+1))
		arr1.append(temp)		

	reqdmap1 = {} #for entities
	reqdmap2 = {} #for events
	reqdmap3 = {} # for both
	for windex in range(len(wratiolist)):
		print " weight", windex
		reqdmap1[arr1[windex][0]] = return_muc(kenlist, kevlist, a, b, c, d, 0, wratiolist[windex])
		reqdmap2[arr1[windex][0]] = return_muc(kenlist, kevlist, a, b, c, d, 1, wratiolist[windex])
		reqdmap3[arr1[windex][0]] = return_muc(kenlist, kevlist, a, b, c, d, 2, wratiolist[windex])

		reqdmap1[arr1[windex][1]] = return_bcub( kenlist, kevlist, a, b, c, d, 0, wratiolist[windex])
		reqdmap2[arr1[windex][1]] = return_bcub( kenlist, kevlist, a, b, c, d, 1, wratiolist[windex])
		reqdmap3[arr1[windex][1]] = return_bcub( kenlist, kevlist, a, b, c, d, 2, wratiolist[windex])
		
		reqdmap1[arr1[windex][2]] = return_ceafe( kenlist, kevlist, a, b, c, d, 0, wratiolist[windex])
		reqdmap2[arr1[windex][2]] = return_ceafe( kenlist, kevlist, a, b, c, d, 1, wratiolist[windex])
		reqdmap3[arr1[windex][2]] = return_ceafe( kenlist, kevlist, a, b, c, d, 2, wratiolist[windex])

		reqdmap1[arr1[windex][3]] = return_blanc(kenlist, kevlist, a, b, c, d, 0, wratiolist[windex])
		reqdmap2[arr1[windex][3]] = return_blanc(kenlist, kevlist, a, b, c, d, 1, wratiolist[windex])
		reqdmap3[arr1[windex][3]] = return_blanc(kenlist, kevlist, a, b, c, d, 2, wratiolist[windex])

	savemat(str(topid) + "_onlyentity.mat", reqdmap1)
	savemat(str(topid) + "_onlyevent.mat", reqdmap2)
	savemat(str(topid) + "_both.mat", reqdmap3)
	
	print reqdmap1
	print 
	print reqdmap2
	print 
	print reqdmap3
 
if __name__ == "__main__":
	main()

