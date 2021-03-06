import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as colit
import os
import scipy.io as sio

def plotit(kenlist, kevlist, topid, data, title, outputfile):
	newdata = []
	row, col = data.shape
	for i in range(row):
		temp = []
		for j in range(col):
			temp.append(float(data[i,j]))
		newdata.append(temp)

	data = np.array(newdata)
	cmap = colit.get_cmap('Purples', 14)
	plt.clf()
	plt.imshow(data, interpolation = 'nearest', cmap = cmap, origin = 'lower', extent = [kenlist[0], kenlist[-1], kevlist[0], kevlist[-1]], aspect = 'auto')
	plt.colorbar()
	plt.xlabel('Number of entity clusters')
	plt.ylabel('Number of event clusters')
	plt.title(title)
	plt.savefig(outputfile)
	 

def main():
	kenlist = range(15,61,5)
	kevlist = range(4,41,4)
	topid = 6


	typesf = ['onlyentity', 'onlyevent', 'both']		
	w = [1,2,3]
	namelst = ['muc', 'bcub', 'ceafe', 'blanc']

	oppath = 'heatmaps/topic' + str(topid) +"/"
	os.system("mkdir -p " + oppath)
	for k in typesf:
	  hm = sio.loadmat(str(topid) + "_" + k + ".mat")
	
	  for i in range(len(w)):
		for scoremetric in namelst:
			key  = scoremetric + "_w" + str(w[i])
			title =  scoremetric.upper() + "-" + "Topic:" + str(topid) + "-w" + str(w[i]) + "-" + k
			fname = oppath + scoremetric + "_topic" + str(topid) + "_w" + str(w[i]) + "_" + k
		#	print hm[key]
			plotit(kenlist, kevlist, topid, hm[key], title , fname)
	
if __name__ == "__main__":
	main()
