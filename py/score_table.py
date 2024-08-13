#!/usr/bin/python3

import sys
from os import listdir
from os.path import isfile, join

int_dir = "/z/int/muscle_benchmark/"
int_dir2 = "/z/int/muscle_benchmark2/"
res_dir = "/z/a/res/muscle_benchmark/"
bench_algos_dir = res_dir + "bench_algos/"
accs_dir = res_dir + "accs/"
qscores_dir = int_dir2 + "qscores/"
msta_scores_dir = int_dir2 + "msta_scores/"

# benchmarks
bs = [ "balibase", "homstrad", "balifam100", "balifam1000", "balifam10000" ]

def read_lines(fn):
	return [ line.strip() for line in open(fn) ]

# return pathnames of regular files in a directory
def read_dir(path):
	return [fn for fn in listdir(path) if isfile(join(path, fn))]

'''
set=BB11014     q=0.8040        tc=0.6895
set=BB11016     q=0.8097        tc=0.5545
set=BB11018     q=0.7292        tc=0.5248
'''
def read_qscores(b, algo):
	try:
		f = open(qscores_dir + b + "/" + algo)
	except:
		return {}
	acc2tc = {}
	for line in f:
		if not line.startswith("set="):
			continue
		flds = line.strip().split("\t")
		acc = flds[0].replace("set=", "")
		tc = float(flds[2][3:])
		acc2tc[acc] = tc
	return acc2tc

'''
aln=z:/int/muscle_benchmark/output_msas/balibase/clustalo/BB11001  Z=5.483  LDDT_mu=0.7120
'''
def read_msta_scores(b, algo):
	acc2z = {}
	acc2lddt_mu = {}
	try:
		f = open(msta_scores_dir + b + "/" + algo)
	except:
		return {}, {}
	for line in f:
		if not line.startswith("aln="):
			continue
		flds = line.strip().split("\t")
		Z = None
		LDDT_mu = None
		for fld in flds:
			if fld.startswith("aln="):
				acc = fld.replace("aln=", "").split("/")[-1]
			elif fld.startswith("Z="):
				Z = float(fld.replace("Z=", ""))
			elif fld.startswith("LDDT_mu="):
				LDDT_mu = float(fld.replace("LDDT_mu=", ""))
		acc2z[acc] = Z
		acc2lddt_mu[acc] = LDDT_mu

	return acc2z, acc2lddt_mu

def get_str(dict, key, fmt, missing):
	try:
		x = dict[key]
	except:
		return missing
	return fmt % x

for b in bs:
	accs = read_lines(accs_dir + b)
	algos = read_lines(bench_algos_dir + b)
	metric_to_NA_count = {}
	metric_to_OK_count = {}

	for algo in algos:
		sys.stderr.write(b + " " + algo + "\n")

		metrics = [ "tc", "z", "lddt_mu" ]
		for metric in metrics:
			metric_to_NA_count[metric] = 0
			metric_to_OK_count[metric] = 0

		acc2tc = read_qscores(b, algo)
		acc2z, acc2lddt_mu = read_msta_scores(b, algo)
		for acc in accs:
			stc = get_str(acc2tc, acc, "%.4f", "NA")
			sz = get_str(acc2z, acc, "%.3f", "NA")
			slddt_mu = get_str(acc2lddt_mu, acc, "%.4f", "NA")

			if stc == "NA":
				metric_to_NA_count["tc"] += 1
			else:
				metric_to_OK_count["tc"] += 1

			if sz == "NA":
				metric_to_NA_count["z"] += 1
			else:
				metric_to_OK_count["z"] += 1

			if slddt_mu == "NA":
				metric_to_NA_count["lddt_mu"] += 1
			else:
				metric_to_OK_count["lddt_mu"] += 1

			s = "bench=" + b
			s += "\talgo=" + algo
			s += "\tacc=" + acc
			s += "\ttc=" + stc
			s += "\tz=" + sz 
			s += "\tlddt_mu=" + slddt_mu
			print(s)

		for metric in metrics:
			if metric == "tc" and b.startswith("balifam"):
				continue
			s = "metric=" + metric
			s += "\tbench=" + b
			s += "\talgo=" + algo
			s += "\tnr_na=" + str(metric_to_NA_count[metric])
			s += "\tnr_ok=" + str(metric_to_OK_count[metric])
			print(s)
