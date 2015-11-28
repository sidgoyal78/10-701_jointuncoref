import numpy as np
from nltk.corpus import wordnet as wn
from collections import OrderedDict as OD


def get_lxvector_wn(word):
	ssets = wn.synsets(word)
	reqvec = OD([(u'adj.all', 0), (u'adj.pert', 0), (u'adj.ppl', 0), (u'adv.all', 0), (u'noun.Tops', 0), (u'noun.act', 0), (u'noun.animal', 0), (u'noun.artifact', 0), (u'noun.attribute', 0), (u'noun.body', 0), (u'noun.cognition', 0), (u'noun.communication', 0), (u'noun.event', 0), (u'noun.feeling', 0), (u'noun.food', 0), (u'noun.group', 0), (u'noun.location', 0), (u'noun.motive', 0), (u'noun.object', 0), (u'noun.person', 0), (u'noun.phenomenon', 0), (u'noun.plant', 0), (u'noun.possession', 0), (u'noun.process', 0), (u'noun.quantity', 0), (u'noun.relation', 0), (u'noun.shape', 0), (u'noun.state', 0), (u'noun.substance', 0), (u'noun.time', 0), (u'verb.body', 0), (u'verb.change', 0), (u'verb.cognition', 0), (u'verb.communication', 0), (u'verb.competition', 0), (u'verb.consumption', 0), (u'verb.contact', 0), (u'verb.creation', 0), (u'verb.emotion', 0), (u'verb.motion', 0), (u'verb.perception', 0), (u'verb.possession', 0), (u'verb.social', 0), (u'verb.stative', 0), (u'verb.weather', 0)])

	for i in ssets:
		reqvec[i.lexname()] = 1
	return reqvec.values()



### testing
print get_lxvector_wn('walk')		
