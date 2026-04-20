#!/bin/bash
#SBATCH --time=24:00:00   # walltime.  hours:minutes:seconds
#SBATCH --gpus=0
#SBATCH --mem-per-cpu=32000M 
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user %u@byu.edu
#SBATCH --output %j_%x.out
#SBATCH --qos=matrix
#SBATCH --job-name=make_charlotte_1.0_train_data

bash data/make_training_data.sh