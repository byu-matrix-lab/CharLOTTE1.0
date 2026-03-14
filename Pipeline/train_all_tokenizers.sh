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
#SBATCH --output Pipeline/slurm_outputs/slurm_outputs/%j_%x.out
#SBATCH --job-name=train_all_tokenizers
#SBATCH --qos matrix

source .env

rm -r ${DATA_HOME}/CognateMT/spm_models/*
rm ${DATA_HOME}/CognateMT/spm_models/notes

set -e

for FILE in Pipeline/cfg/tok/*; do
    if [ $FILE == "Pipeline/cfg/tok/archive"  ]
    then
        continue
    fi
    echo "##################################################################################################################################"
    echo "    train_srctgt_tokenizer.sh ${FILE}"
    bash Pipeline/train_srctgt_tokenizer.sh $FILE
    echo "Finished Tokenizer-------------"
    echo "(${FILE})"
    date
    echo "-------------------------------"


    echo ""
    echo ""
    echo ""
    echo ""
    echo ""
    echo ""
    echo ""
    echo ""
done

echo "Created by Pipeline/train_all_tokenizers.sh" > ${DATA_HOME}/CognateMT/spm_models/notes
date >> ${DATA_HOME}/CognateMT/spm_models/notes

python Pipeline/clean_slurm_outputs.py
