from pckmeans_with_writer import PCKMeans
from label_extractor import extract_labels_for_scoring
import subprocess
####################



def runscore(topid, kenlist, kevlist, wratiolist, cmd):
	numiter = 10
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
	
	
		
	print lstscore1
	print
	print lstscore2
	print
	print lstscore3
	return (lstscore1, lstscore2, lstscore3)

def writeout(fptr, kenlist, kevlist, a, b, c, ind):
	str1 = "0," 
	strlist = [str(i) for i in kenlist]
	str1 = str1 + ",".join(strlist) + "\n"
	fptr.write(str1)
	for i in kevlist:
		str2 = str(i) + ","
		val = []
		for j in kenlist:
			val.append(str( round( ( (a[ind][(j, i, 1, 2, 4)] + b[ind][(j, i, 1,2,4)] + c[ind][(j,i, 1,2,4)]) / 3.0), 2)))
		str2 = str2 + ",".join(val) + "\n"
		fptr.write(str2)


def main():
	kenlist = range(4, 53, 4) # [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52]
	kevlist = range(3, 31, 3) 
	wratiolist = [(1,2,4)]	#3-tuple with (w_tiny,w_small,w_large)
	topid = 42
	a = runscore(topid, kenlist, kevlist, wratiolist, 'muc')
	b = runscore(topid, kenlist, kevlist, wratiolist, 'bcub')
	c = runscore(topid, kenlist, kevlist, wratiolist, 'ceafe')
	
	# first line
	f1 = open(str(topid) + '_onlyent.csv', 'w')
	f2 = open(str(topid) + '_onlyevt.csv', 'w')
	f3 = open(str(topid) + '_both.csv', 'w')
	
	writeout(f1, kenlist, kevlist, a, b, c, 0)
	writeout(f2, kenlist, kevlist, a, b, c, 1)
	writeout(f3, kenlist, kevlist, a, b, c, 2)

	f1.close()
	f2.close()
	f3.close()
if __name__ == "__main__":
	main()

