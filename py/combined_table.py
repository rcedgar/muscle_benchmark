#!/usr/bin/python3

import sys

bs = [ "balibase", "homstrad", "balifam100", "balifam1000", "balifam10000" ]
metrics = [ "tc", "z", "lddt_mu" ]

# make dict from tab-separated fields name=value
def line2dict(line):
	flds = line.strip().split('\t')
	d = {}
	for fld in flds:
		flds2 = fld.split('=')
		if len(flds2) == 2:
			d[flds2[0]] = flds2[1]
	return d

b2accs = {}
b2algos = {}
for b in bs:
	b2accs[b] = set()
	b2algos[b] = set()

baam2value = {}

# bench=balibase  algo=clustalo   acc=BB11001     tc=0.9123       z=5.483 lddt_mu=0.7120
for line in open("../results/score_table.tsv"):
	d = line2dict(line)
	b = d.get("bench")
	algo = d.get("algo")
	acc = d.get("acc")
	if b not in bs:
		continue
	if acc is None:
		continue
	if algo not in b2algos[b]:
		b2algos[b].add(algo)
	if acc not in b2accs[b]:
		b2accs[b].add(acc)
	for metric in metrics:
		value = d.get(metric)
		if value is None or value == "NA":
			continue
		baam = (b, algo, acc, metric)
		baam2value[baam] = float(value)

if 0:
	for baam in list(baam2value.keys()):
		print(baam, baam2value[baam])

def get_value(x):
	return x[1]

def skip(b, metric):
	return metric == "tc" and b.startswith("balifam")

for b in bs:
	algos = b2algos[b]
	accs = b2accs[b]
	metric2algo2avg = {}
	metric2algo2n = {}
	for metric in metrics:
		metric2algo2avg[metric] = {}
		metric2algo2n[metric] = {}
		for algo in algos:
			metric2algo2n[algo] = {}
			values = []
			for acc in accs:
				baam = (b, algo, acc, metric)
				value = baam2value.get(baam)
				if not value is None:
					values.append(value)
			n = len(values)
			metric2algo2n[metric][algo] = n
			if n == 0:
				metric2algo2avg[metric][algo] = 0
			else:
				metric2algo2avg[metric][algo] = sum(values)/n
	sorted_algos = sorted(metric2algo2avg["lddt_mu"].items(), key=get_value, reverse=True)
	print("")
	nr_accs = len(accs)
	print("=== %s (%d) ===" % (b, nr_accs))
	partials = set()
	METHOD_FMT = "%16.16s"
	s = METHOD_FMT % "Method"
	for metric in metrics:
		if skip(b, metric):
			continue
		s += "  %8.8s" % (metric)
	print(s)
	for algo, avg in sorted_algos:
		s = METHOD_FMT % algo
		any = False
		for metric in metrics:
			if skip(b, metric):
				continue
			n = metric2algo2n[metric].get(algo, 0)
			if nr_accs - n > 3:
				if n > 3:
					partials.add(algo)
				continue
			avg = metric2algo2avg[metric].get(algo)
			if avg is None:
				s += "  %8.8s       " % "NA"
			else:
				any = True
				# s += "  %8.4f(%5d)" % (avg, n)
				s += "  %8.4f" % (avg)
		if any:
			print(s)
	if len(partials) > 0:
		s = b + " incomplete: "
		for algo in partials:
			n = metric2algo2n[metric].get(algo, 0)
			avg = metric2algo2avg[metric].get(algo)
			s += " %s(%d)" % (algo, n)
		print(s)
