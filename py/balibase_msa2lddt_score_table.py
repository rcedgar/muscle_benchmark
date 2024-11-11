#!/usr/bin/python3

import sys

algos = [ "clustalo", "foldmason_def", "foldmason_iter", "mafft", "matt", "muscle3", "muscle5", "muscle5_mega", "mustang", "upp2", "usalign" ]

for algo in algos:
	fn = "/z/int/igor_foldmason/" + algo + ".stat"
	for line in open(fn):
		flds = line.strip().split('\t')
		if not flds[0].startswith("BB"):
			continue
		acc = flds[0]
		value = flds[1]
# bench=balibase  algo=clustalo   acc=BB11001     tc=0.9123       z=5.483 lddt_mu=0.7120

		s = "bench=balibase"
		s += "\talgo=" + algo
		s += "\tacc=" + acc
		s += "\tlddt_fm=" + value
		print(s)

