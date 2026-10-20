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
#SBATCH --job-name=token_overlap_spm.fr-oc
#SBATCH --qos matrix

source .env

# fr-oc
python NMT/token_overlap_spm.py \
    --data1 $CHARLOTTE_HOME/NMT/data/CharLOTTE/PLAIN/fr-en/train.csv \
    --spm1 $DATA_HOME/CognateMT/spm_models/fr-oc_en/fr-oc_en/fr-oc_en \
    --data2 $CHARLOTTE_HOME/NMT/data/CharLOTTE/PLAIN/oc-en/train.csv \
    --spm2 $DATA_HOME/CognateMT/spm_models/fr-oc_en/fr-oc_en/fr-oc_en \
    --out "$CHARLOTTE_HOME/NMT/vocab_overlap/results/vocab_overlap_fr-oc.json"

# fr'-oc
python NMT/token_overlap_spm.py \
    --data1 $CHARLOTTE_HOME/NMT/data/CharLOTTE/SC/SC_fr2oc-en/train.csv \
    --spm1 $DATA_HOME/CognateMT/spm_models/SC_fr2oc-oc_en/SC_fr2oc-oc_en/SC_fr2oc-oc_en \
    --sc_model_id_1 FR-OC-RNN-0-RNN-251 \
    --data2 $CHARLOTTE_HOME/NMT/data/CharLOTTE/PLAIN/oc-en/train.csv \
    --spm2 $DATA_HOME/CognateMT/spm_models/SC_fr2oc-oc_en/SC_fr2oc-oc_en/SC_fr2oc-oc_en \
    --out "$CHARLOTTE_HOME/NMT/vocab_overlap/results/vocab_overlap_fr'-oc.json"
