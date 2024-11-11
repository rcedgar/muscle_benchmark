#!/usr/bin/python3

import sys
from scipy.stats import wilcoxon

bench = "balibase"
accs_fn = "../accs/balibase"
metric_name = sys.argv[1]

fn = "../results/score_table_balibase_core.tsv"

f = open(fn)

algos = set()
accs = set()
algo2accs = {}
algo2acc2metric = {}

for line in open(accs_fn):
	accs.add(line.strip())

# make dict from tab-separated fields name=value
def line2dict(line):
	flds = line.strip().split('\t')
	d = {}
	for fld in flds:
		flds2 = fld.split('=')
		if len(flds2) == 2:
			d[flds2[0]] = flds2[1]
	return d

while 1:
	line = f.readline()
	if len(line) == 0:
		break
	d = line2dict(line)
	if d.get("bench") != bench:
		continue
	algo = d.get("algo")
	acc = d.get("acc")
	if acc not in accs:
		continue
	if d is None or algo is None or acc is None:
		continue
	if algo not in algos:
		algos.add(algo)
		algo2accs[algo] = set()
		algo2acc2metric[algo] = {}

	value = d.get(metric_name)
	if value == "NA" or value is None:
		metric = None
	else:
		algo2accs[algo].add(acc)
		metric = float(value)

	algo2acc2metric[algo][acc] = metric
	# if acc == "BB11001":
	# 	print(algo2acc2metric[algo][acc])

N = len(accs)
if 0:
	for algo in algos:
		missing = set()
		for acc in accs:
			if not acc in algo2accs[algo]:
				missing.add(acc)
		if len(missing) > 0:
			print("Missing ", algo, missing)

def get_avg(algo):
	metrics = [ x for x in algo2acc2metric[algo].values() if x != None ]
	n = len(metrics)
	if n == 0:
		return None, None
	avg = sum(metrics)/n
	return n, avg

algo2avg = {}
algo2n = {}
done_algos = []
for algo in algos:
	n, avg = get_avg(algo)
	if n is None:
		continue
	done_algos.append(algo)
	algo2n[algo] = n
	algo2avg[algo] = avg

def get_value(x):
	return x[1]

sorted_algos = sorted(algo2avg.items(), key=get_value, reverse=True)

print(bench + " (full, %d MSAs)" % N)
s = metric_name + "\tn\tmethod"
print(s)
sorted_algo_list = []
for algo, n in sorted_algos:
	n = algo2n[algo]
	if n is None:
		continue
	s = "%.4f" % algo2avg[algo]
	s += "\t%d" % n
	s += "\t" + algo
	if n < N:
		s += " (incomplete)"
	else:
		sorted_algo_list.append(algo)
	print(s)

algo_list = []
vs = []
for algo in sorted_algo_list:
	v = []
	has_none = False
	for acc in accs:
		metric = algo2acc2metric[algo].get(acc)
		if metric is None:
			assert False
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

cmpmx = {}
Pmx = {}
for algo in algo_list:
	cmpmx[algo] = {}
	Pmx[algo] = {}

for i in range(nr_algos):
	algoi = algo_list[i]
	vi = vs[i]
	for j in range(i):
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
			if P < 0.05:
				cmpmx[algoi][algoj] = ">"
				cmpmx[algoj][algoi] = "<"
			else:
				cmpmx[algoi][algoj] = "~"
				cmpmx[algoj][algoi] = "~"

			s = algoi
			s += "\t" + compares
			s += "\t" + algoj
			s += "\t%d" % igt
			s += "\t%d" % jgt
			s += "\t%d" % tie
			s += "\t%.3g" % P
			print(s)
		else:
			if P < 0.05:
				cmpmx[algoi][algoj] = "<"
				cmpmx[algoj][algoi] = ">"
			else:
				cmpmx[algoi][algoj] = "~"
				cmpmx[algoj][algoi] = "~"

			s = algoj
			s += "\t" + compares
			s += "\t" + algoi
			s += "\t%d" % jgt
			s += "\t%d" % igt
			s += "\t%d" % tie
			s += "\t%.3g" % P
			print(s)

		Pmx[algoi][algoj] = P
		Pmx[algoj][algoi] = P

NAME_FMT = "%11.11s"

print()
print()
s = NAME_FMT % bench
s += "  %7.7s" % metric_name
for i in range(0, nr_algos):
	s += "  " + NAME_FMT % algo_list[i]
print(s)
for i in range(nr_algos):
	algoi = algo_list[i]
	avg = algo2avg[algoi]
	s = NAME_FMT % algoi
	s += "  %7.4f" % avg
	for j in range(nr_algos):
		if j == i:
			s += "  " + NAME_FMT % ""
		else:
			algoj = algo_list[j]
			cmp = cmpmx[algoi][algoj]
			P = Pmx[algoi][algoj]
			t = cmp + "%.2g" % P
			s += "  " + NAME_FMT % t
	print(s)
