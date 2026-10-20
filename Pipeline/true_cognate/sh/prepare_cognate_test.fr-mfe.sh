#!/bin/bash

set -e

source .env

source "$(conda info --base)/etc/profile.d/conda.sh"


# Get the etymdb pairs
python CopperMT/CopperMT/pipeline/data/extractor_script_cognates_wCommandline_args.py \
    --path_to_etymdb $CHARLOTTE_HOME/CopperMT/CopperMT/submodules/etymdb/data/split_etymdb \
    --out_path $ETYMDB_HOME \
    --langs 'fr' 'mfe' \
    --data_name "fr_mfe"

wget https://raw.githubusercontent.com/kbatsuren/CogNet/master/CogNet-v2.0.zip -O CogNet-v2.0.zip
unzip CogNet-v2.0.zip


# prepare cognate files
python Pipeline/prepare_cognate_test.py -s "fr" -t "mfe" -d $DATA_HOME -e $ETYMDB_HOME

bash "Pipeline/sbatch/predict/fr-mfe.102.true.cfg.sh"