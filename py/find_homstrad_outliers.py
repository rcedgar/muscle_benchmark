#!/usr/bin/python3

import sys

fn_fm = "/z/int/muscle_benchmark2/qscores/homstrad/foldmason"
fn_mu = "/z/int/muscle_benchmark2/qscores/homstrad/muscle5_mega"

def read_file(fn):
	acc2tc = {}
	for line in open(fn):
		if not line.startswith("set="):
			continue
		flds = line[:-1].split('\t')
		assert flds[0].startswith("set=")
		assert flds[1].startswith("q=")
		assert flds[2].startswith("tc=")
		
		acc = flds[0].split("=")[1]
		tc = float(flds[2].split("=")[1])
		acc2tc[acc] = tc
	return acc2tc

acc2tc_fm = read_file(fn_fm)
acc2tc_mu = read_file(fn_mu)
acc2diff = {}

for acc in list(acc2tc_fm.keys()):
	tc_fm = acc2tc_fm[acc]
	tc_mu = acc2tc_mu[acc]
	acc2diff[acc] = tc_fm - tc_mu

def get_value(x):
	return x[1]

counts = [0]*21
sorted_diffs = sorted(acc2diff.items(), key=get_value, reverse=True)
for acc, diff in sorted_diffs:
	tc_fm = acc2tc_fm[acc]
	tc_mu = acc2tc_mu[acc]
	assert diff == tc_fm - tc_mu
	tenths = int(round(diff*10)) + 10
	assert tenths >= 0 and tenths <= 21
	counts[tenths] += 1

	s = acc
	s += "\t%+.4f" % diff
	s += "\t%.4f" % tc_fm
	s += "\t%.4f" % tc_mu
	print(s)

if 0:
	for tenths in range(0, 21):
		diff = (tenths - 10)/10
		s = "%3.1f" % diff
		s += "\t%u" % counts[tenths]
		print(s)
