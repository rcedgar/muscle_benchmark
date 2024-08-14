#!/usr/bin/python3

assert False, "TODO"

import sys

'''
	 method1          cmp       method2   gt tie lt   P
		   0            1             2    3   4  5   6
muscle5_mega  better-than      clustalo  183  14  0   3.87e-30
	clustalo  (unresolved)     upp2      105  91  1   0.172
	 usalign  better-than      clustalo  173  24  0   7.2e-18
'''

fn = sys.argv[1]

f = open(fn)
for line in (f):
	if line.startswith("method1\tcompares"):
		break

algos = set()
algo2worse = {}
algo2better = {}
algo2tie = {}

for line in (f):
	flds = line.strip().split('\t')
	algo1 = flds[0]
	algo2 = flds[2]
	for algo in [ algo1, algo2 ]:
		if algo not in algos:
			algos.add(algo)
			algo2worse[algo] = []
			algo2better[algo] = []
			algo2tie[algo] = []
	cmp = flds[1]
	P = float(flds[6])
	if cmp == "better-than":
		algo2better[algo1].append((algo2, P))
		algo2worse[algo2].append((algo1, P))
	else:
		algo2tie[algo1].append((algo2, P))
		algo2tie[algo2].append((algo1, P))

def dag(s, algo):
	worse = algo2worse[algo]
	for algo2 in worse:
		s += dag

done = set()
roots = []
for algo in algos:
	if len(algo2worse[algo]) == 0:
		s = ""
		s = dag(s, algo)
		
