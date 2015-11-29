import numpy as np
from nltk.corpus import wordnet as wn
from collections import OrderedDict as OD


def get_wordnet_feat(word):
	ssets = wn.synsets(word)
	reqvec = OD([(u'adj.all', 0), (u'adj.pert', 0), (u'adj.ppl', 0), (u'adv.all', 0), (u'noun.Tops', 0), (u'noun.act', 0), (u'noun.animal', 0), (u'noun.artifact', 0), (u'noun.attribute', 0), (u'noun.body', 0), (u'noun.cognition', 0), (u'noun.communication', 0), (u'noun.event', 0), (u'noun.feeling', 0), (u'noun.food', 0), (u'noun.group', 0), (u'noun.location', 0), (u'noun.motive', 0), (u'noun.object', 0), (u'noun.person', 0), (u'noun.phenomenon', 0), (u'noun.plant', 0), (u'noun.possession', 0), (u'noun.process', 0), (u'noun.quantity', 0), (u'noun.relation', 0), (u'noun.shape', 0), (u'noun.state', 0), (u'noun.substance', 0), (u'noun.time', 0), (u'verb.body', 0), (u'verb.change', 0), (u'verb.cognition', 0), (u'verb.communication', 0), (u'verb.competition', 0), (u'verb.consumption', 0), (u'verb.contact', 0), (u'verb.creation', 0), (u'verb.emotion', 0), (u'verb.motion', 0), (u'verb.perception', 0), (u'verb.possession', 0), (u'verb.social', 0), (u'verb.stative', 0), (u'verb.weather', 0)])

	for i in ssets:
		reqvec[i.lexname()] = 1
	return reqvec.values()

def get_pos_feat(postag):
	reqvector = OD([('CC', 0), ('CD', 0), ('DT', 0), ('EX', 0), ('FW', 0), ('IN', 0), ('JJ', 0), ('JJR', 0), ('JJS', 0), ('LS', 0), ('MD', 0), ('NN', 0), ('NNP', 0), ('NNPS', 0), ('NNS', 0), ('PDT', 0), ('POS', 0), ('PRP', 0), ('PRP$', 0), ('RB', 0), ('RBR', 0), ('RBS', 0), ('RP', 0), ('SYM', 0), ('TO', 0), ('UH', 0), ('VB', 0), ('VBD', 0), ('VBG', 0), ('VBN', 0), ('VBP', 0), ('VBZ', 0), ('WDT', 0), ('WP', 0), ('WP$', 0), ('WRB', 0), ('OTHERS', 0)])
	
	if postag in reqvector:
		reqvector[postag] = 1
	else:		
		reqvector['OTHERS'] = 1

	return reqvector.values()

def get_class_feat(postag):
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

def get_dependency_rellabel(label):
	c = OD([('acl', 0), ('acl:relcl', 0), ('advcl', 0), ('advmod', 0), ('amod', 0), ('appos', 0), ('aux', 0), ('auxpass', 0), ('case', 0), ('cc', 0), ('cc:preconj', 0), ('ccomp', 0), ('compound', 0), ('compound:prt', 0), ('conj', 0), ('cop', 0), ('csubj', 0), ('csubjpass', 0), ('dep', 0), ('det', 0), ('det:predet', 0), ('discourse', 0), ('dislocated', 0), ('dobj', 0), ('expl', 0), ('foreign', 0), ('goeswith', 0), ('iobj', 0), ('list', 0), ('mark', 0), ('mwe', 0), ('name', 0), ('neg', 0), ('nmod', 0), ('nmod:npmod', 0), ('nmod:poss', 0), ('nmod:tmod', 0), ('nsubj', 0), ('nsubjpass', 0), ('nummod', 0), ('parataxis', 0), ('punct', 0), ('remnant', 0), ('reparandum', 0), ('root', 0), ('vocative', 0), ('xcomp', 0), ('others', 0)])	
	if label in c:
		c[label] = 1
	else:
		c['others'] = 1
	return c.values()

