from pckmeans_with_writer import PCKMeans
from label_extractor import extract_labels_for_scoring

####################

if __name__ == '__main__':
	kenlist = [25]
	kevlist = [15]
	wratiolist = [(1,2,4)]	#3-tuple with (w_tiny,w_small,w_large)
	topid = 1
	numiter = 10

	inpfname = 'topic' + str(topid) + '_DS_ordered.pkl'
	for ken in kenlist:
		for kev in kevlist:
			for (wtiny,wsmall,wlarge) in wratiolist:
				pckmeansobj = PCKMeans(inpfname,ken,kev,wlarge,wsmall,wtiny,numiter)

				entonlyintermed = 'entity_only_output/intermediate/int_top' + str(topid) + '_ken' + str(ken) + \
				'_kev' + str(kev) + '_wt' + str(wtiny) +  '_ws' + str(wsmall) + '_wl' + str(wlarge) + '.txt'
				evtonlyintermed = 'event_only_output/intermediate/int_top' + str(topid) + '_ken' + str(ken) + \
				'_kev' + str(kev) + '_wt' + str(wtiny) +  '_ws' + str(wsmall) + '_wl' + str(wlarge) + '.txt'
				entandevtintermed = 'entity_and_event_output/intermediate/int_top' + str(topid) + '_ken' + str(ken) + \
				'_kev' + str(kev) + '_wt' + str(wtiny) +  '_ws' + str(wsmall) + '_wl' + str(wlarge) + '.txt'
				
				pckmeansobj.writelog(entonlyintermed,evtonlyintermed,entandevtintermed)
				del(pckmeansobj)

				entonlyfinal = 'entity_only_output/final/fin_top' + str(topid) + '_ken' + str(ken) + \
				'_kev' + str(kev) + '_wt' + str(wtiny) +  '_ws' + str(wsmall) + '_wl' + str(wlarge) + '.txt'
				evtonlyfinal = 'event_only_output/final/fin_top' + str(topid) + '_ken' + str(ken) + \
				'_kev' + str(kev) + '_wt' + str(wtiny) +  '_ws' + str(wsmall) + '_wl' + str(wlarge) + '.txt'
				entandevtfinal = 'entity_and_event_output/final/fin_top' + str(topid) + '_ken' + str(ken) + \
				'_kev' + str(kev) + '_wt' + str(wtiny) +  '_ws' + str(wsmall) + '_wl' + str(wlarge) + '.txt'

				extract_labels_for_scoring(entonlyintermed,inpfname,entonlyfinal,0)
				extract_labels_for_scoring(evtonlyintermed,inpfname,evtonlyfinal,1)
				extract_labels_for_scoring(entandevtintermed,inpfname,entandevtfinal,2)

	entonlygoldfile = 'entity_only_output/final/top' + str(topid) + '.txt'
	evtonlygoldfile = 'event_only_output/final/top' + str(topid) + '.txt'
	entandevtgoldfile = 'entity_and_event_output/final/top' + str(topid) + '.txt'
	extract_labels_for_scoring('mentions.txt',inpfname,entonlygoldfile,0)
	extract_labels_for_scoring('mentions.txt',inpfname,evtonlygoldfile,1)
	extract_labels_for_scoring('mentions.txt',inpfname,entandevtgoldfile,2) 

