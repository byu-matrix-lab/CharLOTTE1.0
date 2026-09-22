#!/bin/bash

set -e

source .env

source "$(conda info --base)/etc/profile.d/conda.sh"

conda activate char1.0

# Get the etymdb pairs
python CopperMT/CopperMT/pipeline/data/extractor_script_cognates_wCommandline_args.py \
    --path_to_etymdb $CHARLOTTE_HOME/CopperMT/CopperMT/submodules/etymdb/data/split_etymdb \
    --out_path $ETYMDB_HOME \
    --langs 'es' 'an' \
    --data_name "es_an"

# get CogNet Pairs
wget https://raw.githubusercontent.com/kbatsuren/CogNet/master/CogNet-v2.0.zip -O CogNet-v2.0.zip
unzip CogNet-v2.0.zip


# # prepare cognate files
python Pipeline/prepare_cognate_test.py -s "es" -t "an" -d $DATA_HOME -e $ETYMDB_HOME

sbatch "Pipeline/sbatch/predict/es-an.213.true.cfg.sh"
