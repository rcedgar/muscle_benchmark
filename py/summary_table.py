#!/usr/bin/python3

import sys
from scipy.stats import wilcoxon

bench = sys.argv[1]
metric_name = sys.argv[2]
accs_fn = sys.argv[3]

'''
# head score_table.tsv | columns.py
   bench    method      acc      tc        z     z15  lddt_mu  lddt_fm  msa2lddt
balibase  clustalo  BB11001  0.9123    5.483   3.396   0.7120   0.6435    0.6229
balibase  clustalo  BB11002  0.0000   -0.536   1.193   0.6013   0.2209    0.1897
balibase  clustalo  BB11004  0.4076   -4.593   3.136   0.4998   0.3418    0.2775
balibase  clustalo  BB11005  0.1818   -4.021   1.544   0.4359   0.3915    0.3385
'''

fn = "../results/score_table.tsv"

f = open(fn)
hdr_line = f.readline()
flds = hdr_line.strip().split('\t')

fld_nr = None
for i in range(len(flds)):
	if flds[i] == metric_name:
		fld_nr = i
		break
if fld_nr is None:
	sys.stderr.write("Metric not found '%s'\n" % metric_name)
	sys.exit(1)

algos = set()
accs = set()
algo2accs = {}
algo2acc2metric = {}

for line in open(accs_fn):
	accs.add(line.strip())

while 1:
	line = f.readline()
	if len(line) == 0:
		break
	flds = line[:-1].split('\t')
	if flds[0] != bench:
		continue
	algo = flds[1]
	if algo not in algos:
		algos.add(algo)
		algo2accs[algo] = set()
		algo2acc2metric[algo] = {}
		for acc in accs:
			algo2acc2metric[algo][acc] = None

	acc = flds[2]
	if acc not in accs:
		continue
	fld = flds[fld_nr]
	if fld == "NA":
		metric = None
	else:
		algo2accs[algo].add(acc)
		metric = float(fld)

	algo2acc2metric[algo][acc] = metric

N = len(accs)

def get_avg(algo):
	metrics = [ x for x in algo2acc2metric[algo].values() if x != None ]
	n = len(metrics)
	avg = sum(metrics)/n
	return n, avg

algo2avg = {}
algo2n = {}
for algo in algos:
	algo2n[algo], algo2avg[algo] = get_avg(algo)

def get_value(x):
	return x[1]

sorted_algos = sorted(algo2avg.items(), key=get_value, reverse=True)

print(bench + " (full)")
s = metric_name + "\tmethod"
print(s)
for algo, n in sorted_algos:
	n = algo2n[algo]
	s = "%.4f" % algo2avg[algo]
	s += "\t%d" % n
	s += "\t" + algo
	if n < N:
		s += " (incomplete)"
	print(s)

algo_list = []
vs = []
for algo in algos:
	v = []
	has_none = False
	for acc in accs:
		metric = algo2acc2metric[algo][acc]
		if metric is None:
			has_none = True
			break
		v.append(metric)
	if has_none:
		continue
	algo_list.append(algo)
	assert len(v) == N
	vs.append(v)
nr_algos = len(algo_list)

print()
s = "method1"
s += "\tcompares"
s += "\tmethod2"
s += "\tgt"
s += "\tlt"
s += "\ttie"
s += "\tP"
print(s)

for i in range(nr_algos):
	algoi = algo_list[i]
	vi = vs[i]
	for j in range(i + 1, nr_algos):
		algoj = algo_list[j]
		vj = vs[j]
		igt = 0
		jgt = 0
		tie = 0
		for k in range(N):
			if vi[k] > vj[k]:
				igt += 1
			elif vj[k] > vi[k]:
				jgt += 1
			else:
				assert vi[k] == vj[k]
				tie += 1
		stat, P = wilcoxon(vi, vj, alternative="two-sided")
		if P < 0.05:
			compares = "better-than"
		else:
			compares = "(unresolved)"
		if igt > jgt:
			s = algoi
			s += "\t" + compares
			s += "\t" + algoj
			s += "\t%d" % igt
			s += "\t%d" % jgt
			s += "\t%d" % tie
			s += "\t%.3g" % P
			print(s)
		else:
			s = algoj
			s += "\t" + compares
			s += "\t" + algoi
			s += "\t%d" % jgt
			s += "\t%d" % igt
			s += "\t%d" % tie
			s += "\t%.3g" % P
			print(s)
