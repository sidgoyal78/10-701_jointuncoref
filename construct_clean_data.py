import os
import sys
from bs4 import BeautifulSoup

maindir = sys.argv[1]
outputdir = sys.argv[2]
metafile = sys.argv[3]

if not os.path.exists(outputdir):
	os.makedirs(outputdir)

ptr = open(outputdir + "/" + metafile, 'w')

for folder, subs, files in os.walk(maindir):
	if files == []:
		continue

	for f in files:
		filepath = os.path.join(folder, f)
		temptr = open(filepath, 'r')
		content = temptr.read()
		
		### for underscore separated filenames
		newfilename = "_".join(folder.split("/")) + "_" + f
		wrptr = open(outputdir + "/" + newfilename, 'w')
	
		
		soup =  BeautifulSoup(content)
		wrptr.write(soup.get_text())
		wrptr.close()
		temptr.close()
		ptr.write(newfilename + "\n")
	
ptr.close()
		
