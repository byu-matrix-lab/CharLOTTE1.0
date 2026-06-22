#!/bin/bash

set -e

source .env

mkdir -p ${DATA_HOME}
mkdir -p ${DATA_HOME}/CognateMT

source "$(conda info --base)/etc/profile.d/conda.sh"

conda create python=3.10.18 --name char1.0 -y
conda create python=3.8.20 --name cop_mt -y

conda activate cop_mt
pip install -r requirements.copper.txt

conda deactivate
conda activate char1.0
conda install -n char1.0 -c conda-forge cffi pycparser six cld2-cffi icu -y
pip install -r requirements.txt

git clone https://github.com/clab/fast_align.git
cd fast_align
mkdir build
cd build
cmake ..
make

conda deactivate
conda activate cop_mt
conda install boost
cd ../../CopperMT
git clone https://github.com/clefourrier/CopperMT.git
cd CopperMTfiles
python copy_files.py
cd ../CopperMT
git submodule init
git submodule sync
git submodule update
cd submodules/mgiza/mgizapp; cmake . -DBOOST_ROOT=$CONDA_PREFIX; make; make install; cp scripts/merge_alignment.py bin/
cd ../../mosesdecoder; ./bjam -j4 -q -d2 --with-boost=$CONDA_PREFIX

conda deactivate
conda activate char1.0
cd ../../../../data
git clone https://github.com/byu-matrix-lab/data-cleaning-pipeline.git --branch v0.1.0
cd ..
