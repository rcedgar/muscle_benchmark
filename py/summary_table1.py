#!/usr/bin/python3

# Similar to summary table, except one method defines a subset

import sys

bench = sys.argv[1]
metric_name = sys.argv[2]
the_method = sys.argv[3]

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
		accs.add(acc)
	fld = flds[fld_nr]
	if fld == ".":
		metric = None
	else:
		algo2accs[algo].add(acc)
		metric = float(fld)

	algo2acc2metric[algo][acc] = metric

the_accs = algo2accs[the_method]

N = len(the_accs)

def get_avg(algo):
	metrics = []
	for acc in the_accs:
		metric = algo2acc2metric[algo][acc]
		if metric is None:
			return None, None
		metrics.append(metric)
	n = len(metrics)
	avg = sum(metrics)/n
	return n, avg

algo2avg = {}
algo2n = {}
for algo in algos:
	n, avg = get_avg(algo)
	if n is None or avg is None:
		continue
	algo2n[algo] = n
	algo2avg[algo] = avg

def get_value(x):
    return x[1]

sorted_algos = sorted(algo2avg.items(), key=get_value, reverse=True)

print(bench + " (vs. %s)" % the_method)
s = metric_name + "\tmethod"
print(s)
for algo, n in sorted_algos:
	n = algo2n[algo]
	s = "%.4f" % algo2avg[algo]
	s += "\t%d" % n
	s += "\t" + algo
	assert n == N
	print(s)
