#!/bin/bash

#SBATCH --time=24:00:00   # walltime.  hours:minutes:seconds
#SBATCH --nodes=1
#SBATCH --mem=1024000M
#SBATCH --gpus=0
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user %u@byu.edu
#SBATCH --output NMT/slurm_outputs/%j_%x.out
#SBATCH --job-name=metric_oc_diff.uz-kaa
#SBATCH --qos=cs

source .env

python NMT/metric_oc_diff.py \
    --pl_sents $DATA_HOME/data/CharLOTTE_data/uz-en/train.uz.txt \
    --pl_prime_sents $DATA_HOME/data/CharLOTTE_data/uz-en/train.uz.SC_UZ-KAA-RNN-0-RNN-264_uz2kaa.txt \
    --out $CHARLOTTE_HOME/NMT/delta_metrics/results/metric_oc_diff.uz-kaa.txt
