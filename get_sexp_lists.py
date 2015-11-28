import sexpdata


def get_sexp_output(string):
	a = string.split()

	finalstring = ''
	for i in a:
		tillep = i.find(')')
		end = tillep
		if tillep == -1:
			end = len(i)	
		if i[0] == "(":
			finalstring += i[0] + '"' + i[1:end] 
		else:
			finalstring += '"' + i[:end]
		if tillep == -1:
			finalstring += '" ' 
		else:
			finalstring += '"' + i[tillep:] + ' '

	return sexpdata.loads(finalstring)

st2 = '(ROOT (SINV (S (NP (NN Word)) (VP (VBZ comes) (PP (IN from) (NP (NP (NNS People) (NN magazine)) (CC and) (NP (NP (JJ other) (NN celebrity) (NN news) (NNS outlets)) (SBAR (WHNP (WDT that)) (S (NP (NP (NNP Tara) (NNP Reid)) (, ,) (NP (NP (CD 33)) (, ,) (SBAR (WHNP (WP who)) (S (VP (VP (VBD starred) (PP (IN in) (`` ``) (NP (JJ American) (NNP Pie)) ('' ''))) (CC and) (VP (VBD appeared) (PP (IN on) (NP (NP (NNP U.S.) (NN TV) (NN show)) (`` ``) (NP (NNP Scrubs))))))))) (, ,) ('' '')) (VP (VBZ has) (VP (VBN entered) (NP (DT the))))))))))) (VP (VBZ Promises) (NP (NP (NP (NN Treatment) (NN Center)) (PP (IN in) (NP (NNP Malibu) (, ,) (NNP California)))) (: -) (NP (NP (DT the) (JJ same) (NN facility)) (SBAR (WHNP (WDT that)) (S (PP (IN in) (NP (DT the) (NN past))) (VP (VBZ has) (VP (VBN been) (NP (NP (DT the) (NN rehab) (NN facility)) (PP (IN of) (NP (NN choice)))) (PP (IN for) (NP (JJ many)))))))))) (NP (DT a) (NNP Hollywood) (NN star)) (. .)))'

st = '(ROOT (NP (NP (NP (DT Another) (NN day)) (PP (IN in) (NP (NNP Hollywood)))) (: ;) (NP (NP (DT another) (NN star)) (PP (IN in) (NP (NN rehab)))) (. .)))'
print get_sexp_output(st2)
