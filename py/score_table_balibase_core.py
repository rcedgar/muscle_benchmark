#!/usr/bin/python3

import sys
from os import listdir
from os.path import isfile, join

def rename(s):
	if s == "muscle5_mega":
		return "muscle-3d"
	elif s == "muscle5":
		return "muscle-aa"
	elif s == "foldmason_def":
		return "foldmason"
	elif s == "foldmason_iter":
		return "foldmason-i"
	return s

f = open("../results/score_table_balibase_core.tsv", "w")

int_dir = "/z/int/muscle_benchmark/"
int_dir2 = "/z/int/muscle_benchmark2/"
res_dir = "/mnt/c/src/muscle_benchmark/"
bench_algos_dir = res_dir + "bench_algos/"
accs_dir = res_dir + "accs/"
msta_scores_dir = int_dir2 + "msta_balibase_core/"

# benchmarks
bs = [ "balibase" ]

def read_lines(fn):
	return [ line.strip() for line in open(fn) ]

# return pathnames of regular files in a directory
def read_dir(path):
	return [fn for fn in listdir(path) if isfile(join(path, fn))]

'''
aln=z:/int/muscle_benchmark/output_msas/balibase/clustalo/BB11001  Z=5.483  LDDT_mu=0.7120
'''
def read_msta_scores(algo):
	acc2z = {}
	acc2lddt_mu = {}
	try:
		f = open(msta_scores_dir + algo)
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
	algos.append("ref")
	metric_to_NA_count = {}
	metric_to_OK_count = {}

	for algo in algos:
		sys.stderr.write(b + " " + algo + "\n")

		metrics = [ "z", "lddt_mu" ]
		for metric in metrics:
			metric_to_NA_count[metric] = 0
			metric_to_OK_count[metric] = 0

		acc2z, acc2lddt_mu = read_msta_scores(algo)
		for acc in accs:
			sz = get_str(acc2z, acc, "%.3f", "NA")
			slddt_mu = get_str(acc2lddt_mu, acc, "%.4f", "NA")

			if sz == "NA":
				metric_to_NA_count["z"] += 1
			else:
				metric_to_OK_count["z"] += 1

			if slddt_mu == "NA":
				metric_to_NA_count["lddt_mu"] += 1
			else:
				metric_to_OK_count["lddt_mu"] += 1

			s = "bench=" + b
			s += "\talgo=" + rename(algo)
			s += "\tacc=" + acc
			s += "\tz=" + sz 
			s += "\tlddt_mu=" + slddt_mu
			f.write(s + "\n")

		for metric in metrics:
			if metric == "tc" and b.startswith("balifam"):
				continue
			s = "metric=" + metric
			s += "\tbench=" + b
			s += "\talgo=" + rename(algo)
			s += "\tnr_na=" + str(metric_to_NA_count[metric])
			s += "\tnr_ok=" + str(metric_to_OK_count[metric])
			f.write(s + "\n")
f.close()
