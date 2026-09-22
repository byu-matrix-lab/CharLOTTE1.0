#!/bin/bash

#SBATCH --time=24:00:00   # walltime.  hours:minutes:seconds
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=1024000M
#SBATCH --gpus=0
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user %u@byu.edu
#SBATCH --output Pipeline/slurm_outputs/SC_smt/%j_%x.out
#SBATCH --job-name=SC_smt.fr-mfe
#SBATCH --qos cs

python Pipeline/clean_slurm_outputs.py
bash Pipeline/train_SC.sh Pipeline/cfg/SC_SMT/fr-mfe.smt.cfg
python Pipeline/clean_slurm_outputs.py
rm core*

