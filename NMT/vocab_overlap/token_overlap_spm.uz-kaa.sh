#!/bin/bash

#SBATCH --time=24:00:00   # walltime.  hours:minutes:seconds
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=64000M
#SBATCH --gpus=0
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user %u@byu.edu
#SBATCH --output NMT/slurm_outputs/%j_%x.out
#SBATCH --job-name=token_overlap_spm.uz-kaa
#SBATCH --qos matrix

source .env

# uz-kaa
python NMT/token_overlap_spm.py \
    --data1 $CHARLOTTE_HOME/NMT/data/CharLOTTE/PLAIN/uz-en/train.csv \
    --spm1 $DATA_HOME/CognateMT/spm_models/uz-kaa_en/uz-kaa_en/uz-kaa_en \
    --data2 $CHARLOTTE_HOME/NMT/data/CharLOTTE/PLAIN/kaa-en/train.csv \
    --spm2 $DATA_HOME/CognateMT/spm_models/uz-kaa_en/uz-kaa_en/uz-kaa_en \
    --out "$CHARLOTTE_HOME/NMT/vocab_overlap/results/vocab_overlap_uz-kaa.json"

# uz'-kaa
python NMT/token_overlap_spm.py \
    --data1 $CHARLOTTE_HOME/NMT/data/CharLOTTE/SC/SC_uz2kaa-en/train.csv \
    --spm1 $DATA_HOME/CognateMT/spm_models/SC_uz2kaa-kaa_en/SC_uz2kaa-kaa_en/SC_uz2kaa-kaa_en \
    --sc_model_id_1 UZ-KAA-RNN-0-RNN-264 \
    --data2 $CHARLOTTE_HOME/NMT/data/CharLOTTE/PLAIN/kaa-en/train.csv \
    --spm2 $DATA_HOME/CognateMT/spm_models/SC_uz2kaa-kaa_en/SC_uz2kaa-kaa_en/SC_uz2kaa-kaa_en \
    --out "$CHARLOTTE_HOME/NMT/vocab_overlap/results/vocab_overlap_uz'-kaa.json"
