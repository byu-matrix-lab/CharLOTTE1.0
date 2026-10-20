#!/bin/bash

#SBATCH --time=24:00:00   # walltime.  hours:minutes:seconds
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=64000M
#SBATCH --gpus=a100:1
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output bleurt/%j_%x.out
#SBATCH --job-name=run_bleurt
#SBATCH --qos cs
#SBATCH --partition cs

nvidia-smi

bash bleurt/run_bleurt.sh