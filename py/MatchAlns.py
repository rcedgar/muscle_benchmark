#!/usr/bin/python3

import sys

# Author Igor Tolstoy
# https://drive5workspace.slack.com/archives/D076HKBFAM6/p1723128057360849

test_msa_fn = sys.argv[1]
ref_msa_fn = sys.argv[2]

def read_fasta(fn):
  fdict = {}
  with open(fn, "r") as file:
    sels = file.readlines()
    sels = [s.rstrip() for s in sels]
    acc = ""
    for s in sels:
      if ">" in s:
          if acc != "":
              fdict[acc] = seq
          acc = s
          seq = ""
      else:
          seq = seq + s.upper()
  fdict[acc] = seq
  return fdict
refs = {}
tests = {}
refsu = {}
testsu = {}

tests = read_fasta(test_msa_fn)
refs = read_fasta(ref_msa_fn)

for k,v in refs.items():
    s = v.replace(".","").replace("-","").upper()
    refsu[s] = k
for k,v in tests.items():
    s = v.replace(".","").replace("-","").upper()
    testsu[s] = k

pairs = []
for kr,vr in testsu.items():
    v = refsu[kr]
    print(v)
    print(tests[vr])
