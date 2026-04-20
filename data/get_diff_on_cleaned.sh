#!/bin/bash
#SBATCH --time=48:00:00   # walltime.  hours:minutes:seconds
#SBATCH --gpus=0
#SBATCH --mem-per-cpu=32000M 
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user %u@byu.edu
#SBATCH --output /home/hatch5o6/CharLOTTE1.0_public/data/%j_%x.out
#SBATCH --qos=matrix
#SBATCH --job-name=get_diff_on_cleaned



# es-en

file1=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/CCMatrix/es_en/cleaned/src.txt
file2=/home/hatch5o6/nobackup/archive/data/LRRomance/es-en/CCMatrix/fixed/cleaned/src.10M.txt
out=$file1.diff
python data/get_diff.py \
    -f1 $file1 \
    -f2 $file2 > $out

file1=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/CCMatrix/es_en/cleaned/tgt.txt
file2=/home/hatch5o6/nobackup/archive/data/LRRomance/es-en/CCMatrix/fixed/cleaned/tgt.10M.txt
out=$file1.diff
python data/get_diff.py \
    -f1 $file1 \
    -f2 $file2 > $out




# fr-en
file1=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/CCMatrix/fr_en/cleaned/src.txt
file2=/home/hatch5o6/nobackup/archive/data/CCMatrix_fr_en/fixed/stitched/cleaned/src.10M.txt
out=$file1.diff
python data/get_diff.py \
    -f1 $file1 \
    -f2 $file2 > $out

file1=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/CCMatrix/fr_en/cleaned/tgt.txt
file2=/home/hatch5o6/nobackup/archive/data/CCMatrix_fr_en/fixed/stitched/cleaned/tgt.10M.txt
out=$file1.diff
python data/get_diff.py \
    -f1 $file1 \
    -f2 $file2 > $out



# fr-oc
file1=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/nllb/fr_oc/cleaned/src.txt
file2=/home/hatch5o6/nobackup/archive/data/NLLB/fr_oc/cleaned/src.txt
out=$file1.diff
python data/get_diff.py \
    -f1 $file1 \
    -f2 $file2 > $out

file1=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/nllb/fr_oc/cleaned/tgt.txt
file2=/home/hatch5o6/nobackup/archive/data/NLLB/fr_oc/cleaned/tgt.txt
out=$file1.diff
python data/get_diff.py \
    -f1 $file1 \
    -f2 $file2 > $out



# oc-en
file1=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/nllb/oc_en/cleaned/src.txt
file2=/home/hatch5o6/nobackup/archive/data/NLLB/en_oc/cleaned/src.txt
out=$file1.diff
python data/get_diff.py \
    -f1 $file1 \
    -f2 $file2 > $out

file1=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/nllb/oc_en/cleaned/tgt.txt
file2=/home/hatch5o6/nobackup/archive/data/NLLB/en_oc/cleaned/tgt.txt
out=$file1.diff
python data/get_diff.py \
    -f1 $file1 \
    -f2 $file2 > $out
