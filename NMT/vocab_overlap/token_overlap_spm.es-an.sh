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
#SBATCH --job-name=token_overlap_spm.es-an
#SBATCH --qos matrix

source .env

# es-an
python NMT/token_overlap_spm.py \
    --data1 $CHARLOTTE_HOME/NMT/data/CharLOTTE/PLAIN/es-en/train.csv \
    --spm1 $DATA_HOME/CognateMT/spm_models/es-an_en/es-an_en/es-an_en \
    --data2 $CHARLOTTE_HOME/NMT/data/CharLOTTE/PLAIN/an-en/train.csv \
    --spm2 $DATA_HOME/CognateMT/spm_models/es-an_en/es-an_en/es-an_en \
    --out "$CHARLOTTE_HOME/NMT/vocab_overlap/results/vocab_overlap_es-an.json"

# es'-an
python NMT/token_overlap_spm.py \
    --data1 $CHARLOTTE_HOME/NMT/data/CharLOTTE/SC/SC_es2an-en/train.csv \
    --spm1 $DATA_HOME/CognateMT/spm_models/SC_es2an-an_en/SC_es2an-an_en/SC_es2an-an_en \
    --sc_model_id_1 ES-AN-RNN-0-RNN-213 \
    --data2 $CHARLOTTE_HOME/NMT/data/CharLOTTE/PLAIN/an-en/train.csv \
    --spm2 $DATA_HOME/CognateMT/spm_models/SC_es2an-an_en/SC_es2an-an_en/SC_es2an-an_en \
    --out "$CHARLOTTE_HOME/NMT/vocab_overlap/results/vocab_overlap_es'-an.json"
