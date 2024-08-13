#!/usr/bin/python3

import sys

fn = "../results/score_table.tsv"

'''
	   0         1        2       3        4       5        6        7         8
   bench    method      acc      tc        z     z15  lddt_mu  lddt_fm  msa2lddt
balibase  clustalo  BB11001  0.9123    5.483   3.396   0.7120   0.6435    0.6229
balibase  clustalo  BB11002  0.0000   -0.536   1.193   0.6013   0.2209    0.1897
'''

lines = []
fms = []
mus = []
diffs = []
idx2diff = {}
idx = 0
for line in open(fn):
	flds = line[:-1].split('\t')
	try:
		mu = float(flds[6])
		fm = float(flds[8])
	except:
		continue
	lines.append(line[:-1])
	diff = mu - fm
	mus.append(mu)
	fms.append(fm)
	diffs.append(diff)
	idx2diff[idx] = diff
	idx += 1
	
def get_value(x):
	return x[1]

sorted_idxs = sorted(idx2diff.items(), key=get_value)
for idx, diff in sorted_idxs:
	line = lines[idx]
	mu = mus[idx]
	fm = fms[idx]
	s = "diff=%+.4f" % diff
	s += "\tmu=%.4f" % mu
	s += "\tfm=%.4f" % fm
	s += "\t" + line[:32]
	print(s)