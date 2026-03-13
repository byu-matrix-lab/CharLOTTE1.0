#!/bin/bash

set -e
__conda_setup="$('/vapps/rhel9/x86_64/miniconda3/latest/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
eval "$__conda_setup"
unset __conda_setup

conda create python=3.10.18 --name char1.0 -y
conda create python=3.8.20 --name cop_mt -y

conda activate cop_mt
pip install -r requirements.copper.txt

conda deactivate
conda activate char1.0
pip install -r requirements.txt

git clone https://github.com/clab/fast_align.git
cd fast_align
mkdir build
cd build
cmake ..
make

cd ../../CopperMT
git clone https://github.com/clefourrier/CopperMT.git
cd CopperMTfiles
python copy_files.py
cd ../..