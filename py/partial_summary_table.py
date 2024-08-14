#!/usr/bin/python3

# Similar to summary table, except one method defines a subset

import sys
from scipy.stats import wilcoxon

bench = sys.argv[1]
metric_name = sys.argv[2]
the_method = sys.argv[3]

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

algos = set()
accs = set()
algo2accs = {}
algo2acc2metric = {}

for line in open(fn):
	if len(line) == 0:
		break
	d = line2dict(line)
	b = d.get("bench")
	if b != bench:
		continue
	algo = d.get("algo")
	if algo is None:
		continue
	if algo not in algos:
		algos.add(algo)
		algo2accs[algo] = set()
		algo2acc2metric[algo] = {}
		for acc in accs:
			algo2acc2metric[algo][acc] = None

	acc = d.get("acc")
	if acc is None:
		continue
	if acc not in accs:
		accs.add(acc)
	value = d.get(metric_name)
	if value is None:
		continue
	if value == "NA":
		value = None
	else:
		algo2accs[algo].add(acc)
		value = float(value)
	algo2acc2metric[algo][acc] = value

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
	if n == 0:
		return 0, 0
	avg = sum(metrics)/n
	return n, avg

algo2avg = {}
algo2n = {}
for algo in algos:
	n, avg = get_avg(algo)
	if n is None or avg is None:
		continue
#	print(algo, n, avg)
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

algo_list = []
vs = []
for algo in algos:
	v = []
	has_none = False
	for acc in the_accs:
		metric = algo2acc2metric[algo].get(acc)
		if metric is None:
			has_none = True
			break
		v.append(metric)
	if has_none:
		continue
	algo_list.append(algo)
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
		if algoi != the_method and algoj != the_method:
			continue
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
