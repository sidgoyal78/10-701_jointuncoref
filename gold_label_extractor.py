from sys import argv
from feature_extract_class import docStructure

if __name__ == '__main__':
	topid = int(argv[1])
	numtopiddocs = int(argv[2])
	exceptions = []
	for x in argv[3:]:
		exceptions.add(int(x))

	fptr = open('mentions.txt','r')

	for line in fptr:
		if line[0:2] != '##':
			(evoren,top,docid,sentid,corefid,starttokid,endtokid,enccharid) = line.split('\t')


