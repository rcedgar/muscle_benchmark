#!/usr/bin/python3

import sys

bb_acc = sys.argv[1]
outdir = sys.argv[2]

if not outdir.endswith("/"):
	outdir += "/"

bbs_acc = bb_acc.replace("BB", "BBS")

# Full-length BB reference
bb_ref_msa_fn = "/z/int/muscle_benchmark/ref_msas/balibase/" + bb_acc

# Trimmed BB reference
bbs_ref_msa_fn = "/z/a/res/balibase/ref/" + bbs_acc

# Full-length structures
pdb_files_fn = "/z/int/muscle_benchmark/list_files/balibase/" + bb_acc + ".files"

root_dir = "/z/int/muscle_benchmark/"

three2one = { 'ALA':'A', 'VAL':'V', 'PHE':'F', 'PRO':'P', 'MET':'M',
			'ILE':'I', 'LEU':'L', 'ASP':'D', 'GLU':'E', 'LYS':'K',
			'ARG':'R', 'SER':'S', 'THR':'T', 'TYR':'Y', 'HIS':'H',
			'CYS':'C', 'ASN':'N', 'GLN':'Q', 'TRP':'W', 'GLY':'G',
			'MSE':'M' } # MSE translated to M, other special codes ignored

first_chain = None
def read_pdb(fn):
	atom_lines = []
	seq = ""
	first_chain = None
	for line in open(fn):
		if not line.startswith("ATOM "):
			continue
		chain = line[21]
		if first_chain is None:
			first_chain = chain
		else:
			if not chain == first_chain:
				assert False, "Two chains %s %s" % (first_chain, chain)
		element = line[12:16].strip()
		alt_loc = line[16]
		three = line[17:20]
		try:
			one = three2one[three]
		except:
			continue
		if element == "CA":
			if alt_loc == " " or alt_loc == "A" or alt_loc == "1":
				seq += one
				atom_lines.append(line)
	return seq, atom_lines

pdb_seqs = []
pdb_fns = []
atom_lines_vec = []
for line in open(pdb_files_fn):
	pdb_fn = line.strip()
	pdb_path = root_dir + pdb_fn
	seq, atom_lines = read_pdb(pdb_path)
	pdb_seqs.append(seq)
	atom_lines_vec.append(atom_lines)
	pdb_fns.append(pdb_fn)
nr_pdbs = len(pdb_fns)

def read_fasta(fn):
	rows = []
	seqs = []
	labels = []
	label = None
	seq = ""
	for line in open(fn):
		line = line.strip()
		if len(line) == 0:
			continue
		if line[0] == ">":
			if len(seq) > 0:
				rows.append(seq)
				seq = seq.replace("-", "")
				seq = seq.replace(".", "")
				seq = seq.upper()
				seqs.append(seq)
				labels.append(label)
			label = line[1:]
			seq = ""
		else:
			seq += line.replace(" ", "")
	if len(seq) > 0:
		rows.append(seq)
		seq = seq.replace("-", "")
		seq = seq.replace(".", "")
		seq = seq.upper()
		seqs.append(seq)
		labels.append(label)
	return labels, rows, seqs

bb_labels, bb_rows, bb_seqs = read_fasta(bb_ref_msa_fn)
bbs_labels, bbs_rows, bbs_seqs = read_fasta(bbs_ref_msa_fn)

nr_bb_ref_seqs = len(bb_labels)
nr_bbs_ref_seqs = len(bbs_labels)

pdb_idx_to_bb_idx = [None]*nr_pdbs
bb_idx_to_bbs_idx = []
bb_idx_to_pdb_idx = []
bb_idx_to_bbs_pos = []
for bb_idx in range(nr_bb_ref_seqs):
	bb_seq = bb_seqs[bb_idx]
	bbs_idx = None
	bbs_pos = None
	pdb_idx = None

	for idx in range(nr_pdbs):
		if pdb_seqs[idx] == bb_seq:
			pdb_idx = idx
			pdb_idx_to_bb_idx[pdb_idx] = bb_idx
			break

	for bbs_idx2 in range(nr_bbs_ref_seqs):
		bbs_seq = bbs_seqs[bbs_idx2]
		bbs_label = bbs_labels[bbs_idx2]
		pos = bb_seq.find(bbs_seq)
		if pos >= 0:
			if not bbs_pos is None:
				sys.stderr.write("\nERROR: %s Two substring matches >%s\n" % (bb_acc, bbs_label))
				sys.exit(0)		
			bbs_idx = bbs_idx2
			bbs_pos = pos

	bb_idx_to_bbs_idx.append(bbs_idx)
	bb_idx_to_pdb_idx.append(pdb_idx)
	bb_idx_to_bbs_pos.append(bbs_pos)

for idx in range(nr_pdbs):
	if pdb_idx_to_bb_idx[idx] is None:
		sys.stderr.write("\nERROR: PDB %s not matched\n" % pdb_fns[idx])
		sys.exit(1)

if 0:
	print("Full-length MSA BB%s" % bb_acc)
	for idx in range(nr_bb_ref_seqs):
		print()
		print("Reference[%3d] >%s" % (idx, bb_labels[idx]))
		print("Row            %s" % bb_rows[idx])
		print("Seq            %s" % bb_seqs[idx])

	print()
	print("Trimmed MSA BBS%s" % bbs_acc)
	for idx in range(nr_bbs_ref_seqs):
		print()
		print("Reference[%3d] >%s" % (idx, bbs_labels[idx]))
		print("Row            %s" % bbs_rows[idx])
		print("Seq            %s" % bbs_seqs[idx])

	print()
	print("Matches")
	for bb_idx in range(nr_bb_ref_seqs):
		bb_label = bb_labels[bb_idx]
		bbs_idx = bb_idx_to_bbs_idx[bb_idx]
		bbs_label = bbs_labels[bbs_idx]
		bbs_pos = bb_idx_to_bbs_pos[bb_idx]
		pdb_idx = bb_idx_to_pdb_idx[bb_idx]
		pdb_fn = pdb_fns[pdb_idx]
		bb_seq = bb_seqs[bbs_idx]
		atom_lines = atom_lines_vec[pdb_idx]
		assert len(bb_seq) == len(atom_lines)
		print(bb_label, bbs_label, bbs_idx, bbs_pos, pdb_idx, pdb_fn)

####################################
# validate matches		
####################################
for bb_idx in range(nr_bb_ref_seqs):
	bbs_idx = bb_idx_to_bbs_idx[bb_idx]
	bb_label = bb_labels[bb_idx]
	bb_seq = bb_seqs[bb_idx]
	bbs_seq = bbs_seqs[bbs_idx]
	bbs_idx = bb_idx_to_bbs_idx[bb_idx]
	bbs_label = bbs_labels[bbs_idx]
	bbs_pos = bb_idx_to_bbs_pos[bb_idx]
	pdb_idx = bb_idx_to_pdb_idx[bb_idx]
	pdb_fn = pdb_fns[pdb_idx]
	pdb_seq = pdb_seqs[pdb_idx]
	bbs_seq = bbs_seqs[bbs_idx]
	atom_lines = atom_lines_vec[pdb_idx]
	if len(bb_seq) != len(atom_lines):
		sys.stderr.write("\nERROR -- len(bb_seq) != len(atom_lines)\n")
		sys.stderr.write("bb_label=%s\n" % bb_label)
		sys.stderr.write("pdb_fn=%s\n" % pdb_fn)
		sys.stderr.write("pdb_seq=%s\n" % pdb_seq)
		sys.stderr.write("bb_seq=%s\n" % bb_seq)
		sys.stderr.write("bbs_pos=%d\n" % bbs_pos)
		sys.stderr.write("len(bb_seq)=%d\n" % len(bb_seq))
		sys.stderr.write("len(atom_lines)=%d\n" % len(atom_lines))
		assert False

	hi = len(bbs_seq) + bbs_pos
	if  hi > len(bb_seq):
		sys.stderr.write("\nERROR -- hi=%d > len(bb_seq)=%d\n" % (hi, len(bb_seq)))
		sys.stderr.write("bb_label=%s\n" % bb_label)
		sys.stderr.write(" pdb_fn=%s\n" % pdb_fn)
		sys.stderr.write("pdb_seq=%s\n" % pdb_seq)
		sys.stderr.write(" bb_seq=%s\n" % bb_seq)
		sys.stderr.write("bbs_pos=%d\n" % bbs_pos)
		sys.stderr.write("len(bb_seq)=%d\n" % len(bb_seq))
		sys.stderr.write("len(bbs_seq)=%d\n" % len(bbs_seq))
		sys.stderr.write("len(atom_lines)=%d\n" % len(atom_lines))
		assert False

trimmed_ref_msa_fn = outdir + bbs_acc + ".refmsa"
try:
	f = open(trimmed_ref_msa_fn, "w")
except:
	f = None
if f is None:
	sys.stderr.write("Not found, skipping %s\n" % trimmed_ref_msa_fn)
	sys.exit(0)
for bb_idx in range(nr_bb_ref_seqs):
	label = bb_labels[bb_idx]
	bbs_idx = bb_idx_to_bbs_idx[bb_idx]
	bbs_row = bbs_rows[bbs_idx]
	f.write(">" + label + "\n")
	f.write(bbs_row + "\n")
f.close()

trimmed_pdb_fns = []
for bb_idx in range(nr_bb_ref_seqs):
	pdb_idx = bb_idx_to_pdb_idx[bb_idx]
	bbs_idx = bb_idx_to_bbs_idx[bb_idx]
	bbs_pos = bb_idx_to_bbs_pos[bb_idx]

	pdb_fn = pdb_fns[pdb_idx]
	bb_seq = bb_seqs[bb_idx]
	bbs_seq = bbs_seqs[bbs_idx]
	atom_lines = atom_lines_vec[pdb_idx]

	pdb_name = pdb_fn.split('/')[-1]
	bb_seq_len = len(bb_seq)
	assert(bb_seq_len == len(atom_lines))
	bbs_seq_len = len(bbs_seq)
	trimmed_pdb_fn = outdir + pdb_name
	trimmed_pdb_fns.append(trimmed_pdb_fn)

	bbs_seq = bbs_seqs[bbs_idx]
	atom_lines = atom_lines_vec[pdb_idx]
	hi = len(bbs_seq) + bbs_pos
	f = open(trimmed_pdb_fn, "w")
	for i in range(bbs_pos, hi):
		f.write(atom_lines[i])
	f.close()
assert len(trimmed_pdb_fns) == nr_bb_ref_seqs

f = open(outdir + bbs_acc + ".files", "w")
trimmed_labels, trimmed_rows, trimmed_seqs = read_fasta(trimmed_ref_msa_fn)
for bb_idx in range(nr_bb_ref_seqs):
	pdb_idx = bb_idx_to_pdb_idx[bb_idx]
	trimmed_seq = trimmed_seqs[bb_idx]
	trimmed_pdb_fn = trimmed_pdb_fns[bb_idx]
	seq, atom_lines = read_pdb(trimmed_pdb_fn)
	assert seq == trimmed_seq
	name = trimmed_pdb_fn.split('/')[-1]
	f.write(name + "\n")
f.close()