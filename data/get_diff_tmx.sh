#!/bin/bash
#SBATCH --time=48:00:00   # walltime.  hours:minutes:seconds
#SBATCH --gpus=0
#SBATCH --mem-per-cpu=128000M 
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user %u@byu.edu
#SBATCH --output /home/hatch5o6/CharLOTTE1.0_public/data/%j_%x.out
#SBATCH --qos=matrix
#SBATCH --job-name=get_diff_tmx



# file1=/home/hatch5o6/nobackup/archive/data/CCMatrix_fr_en/fixed/stitched/en-fr.fixed.ending.STITCHED.tmx
# file2=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/CCMatrix/fr_en/en-fr.tmx
# out=$file1.diff
# python data/get_diff.py \
#     -f1 $file1 \
#     -f2 $file2 > $out

file1=/home/hatch5o6/nobackup/archive/data/LRRomance/es-en/CCMatrix/fixed/en-es.fixed.ending.tmx
file2=/home/hatch5o6/nobackup/archive/data/CharLOTTE1.0_NEW_REPO/data/raw/CCMatrix/es_en/en-es.tmx
out=$file1.diff
python data/get_diff.py \
    -f1 $file1 \
    -f2 $file2 > $out
