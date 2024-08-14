#!/usr/bin/python3

import sys

fn = "../results/score_table.tsv"

# make dict from tab-separated fields name=value
def line2dict(line):
	flds = line.strip().split('\t')
	d = {}
	for fld in flds:
		flds2 = fld.split('=')
		if len(flds2) == 2:
			d[flds2[0]] = flds2[1]
	return d

lines = []
fms = []
mus = []
diffs = []
idx2diff = {}
idx = 0
for line in open(fn):
	d = line2dict(line)
	mu = d.get("lddt_mu")
	fm = d.get("lddt_mf")
	if mu is None or fm is None:
		continue
	diff = mu - fm
	mus.append(mu)
	fms.append(fm)
	diffs.append(diff)
	idx2diff[idx] = diff
	idx += 1
n = len(diffs)
sys.stderr.write("%d pairs\n" % n)
	
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