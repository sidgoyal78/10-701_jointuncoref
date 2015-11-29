import numpy as np
from nltk.corpus import wordnet as wn
from collections import OrderedDict as OD


def get_lxvector_wordnet(word):
	ssets = wn.synsets(word)
	reqvec = OD([(u'adj.all', 0), (u'adj.pert', 0), (u'adj.ppl', 0), (u'adv.all', 0), (u'noun.Tops', 0), (u'noun.act', 0), (u'noun.animal', 0), (u'noun.artifact', 0), (u'noun.attribute', 0), (u'noun.body', 0), (u'noun.cognition', 0), (u'noun.communication', 0), (u'noun.event', 0), (u'noun.feeling', 0), (u'noun.food', 0), (u'noun.group', 0), (u'noun.location', 0), (u'noun.motive', 0), (u'noun.object', 0), (u'noun.person', 0), (u'noun.phenomenon', 0), (u'noun.plant', 0), (u'noun.possession', 0), (u'noun.process', 0), (u'noun.quantity', 0), (u'noun.relation', 0), (u'noun.shape', 0), (u'noun.state', 0), (u'noun.substance', 0), (u'noun.time', 0), (u'verb.body', 0), (u'verb.change', 0), (u'verb.cognition', 0), (u'verb.communication', 0), (u'verb.competition', 0), (u'verb.consumption', 0), (u'verb.contact', 0), (u'verb.creation', 0), (u'verb.emotion', 0), (u'verb.motion', 0), (u'verb.perception', 0), (u'verb.possession', 0), (u'verb.social', 0), (u'verb.stative', 0), (u'verb.weather', 0)])

	for i in ssets:
		reqvec[i.lexname()] = 1
	return reqvec.values()

def get_pos_features(postag):
	reqvector = OD([('CC', 0), ('CD', 0), ('DT', 0), ('EX', 0), ('FW', 0), ('IN', 0), ('JJ', 0), ('JJR', 0), ('JJS', 0), ('LS', 0), ('MD', 0), ('NN', 0), ('NNP', 0), ('NNPS', 0), ('NNS', 0), ('PDT', 0), ('POS', 0), ('PRP', 0), ('PRP$', 0), ('RB', 0), ('RBR', 0), ('RBS', 0), ('RP', 0), ('SYM', 0), ('TO', 0), ('UH', 0), ('VB', 0), ('VBD', 0), ('VBG', 0), ('VBN', 0), ('VBP', 0), ('VBZ', 0), ('WDT', 0), ('WP', 0), ('WP$', 0), ('WRB', 0), ('OTHERS', 0)])
	
	if postag in reqvector:
		reqvector[postag] = 1
	else:		
		reqvector['OTHERS'] = 1

	return reqvector.values()

def get_class_features(postag):
	reqlist = [0]*4  #[verb, noun, adj, other]

	if postag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
		reqlist[0] = 1
	elif postag in ['NN', 'NNP', 'NNPS', 'NNS']:
		reqlist[1] = 1
	elif postag in ['JJ', 'JJR', 'JJS']:
		reqlist[2] = 1
	else:
		reqlist[3] = 1
	
	return reqlist
	
### testing
print get_lxvector_wordnet('walk')
print 
print get_pos_features('NNP')
print
print get_class_features('NNP')
