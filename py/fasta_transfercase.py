#!/usr/bin/python3

import sys
import fasta

FileName1 = sys.argv[1]
FileName2 = sys.argv[2]

seqs1 = []
ungapped_upper_seqs1 = []
seqs2 = []
ungapped_upper_seqs2 = []
labels1 = []
labels2 = []

def OnSeq1(label, seq):
	labels1.append(label)
	seqs1.append(seq)
	u = seq.replace('-', '')
	u = u.replace('.', '')
	ungapped_upper_seqs1.append(u.upper())

def OnSeq2(label, seq):
	labels2.append(label)
	seqs2.append(seq)
	u = seq.replace('-', '')
	u = u.replace('.', '')
	ungapped_upper_seqs2.append(u.upper())
	
fasta.ReadSeqsOnSeq(FileName1, OnSeq1)
fasta.ReadSeqsOnSeq(FileName2, OnSeq2)

def Transfer(Seq, AlignedSeq):
	j = 0
	s = ""
	for i in range(0, len(AlignedSeq)):
		c = AlignedSeq[i]
		if c == "-" or c == ".":
			s += c
		else:
			d = Seq[j]
			assert d.upper() == c.upper()
			s += Seq[j]
			j += 1
	return s

for idx2 in range(len(seqs2)):
	seq2 = seqs2[idx2]
	u2 = ungapped_upper_seqs2[idx2]
	idx1 = None
	for idx in range(len(labels1)):
		if ungapped_upper_seqs1[idx] == u2:
			idx1 = idx
			break
	assert not idx1 is None
	fixed_seq2 = Transfer(seqs1[idx1], seqs2[idx2])
	fasta.WriteSeq(sys.stdout, fixed_seq2, labels2[idx2])


		  
