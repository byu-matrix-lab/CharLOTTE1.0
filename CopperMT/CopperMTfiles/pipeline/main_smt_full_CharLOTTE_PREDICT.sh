#!/bin/bash

# Original work: CopperMT (https://github.com/clefourrier/CopperMT)
# by Clémentine Fourrier (clefourrier), licensed under GNU GPL 3.
#
# Modified by Brendan Hatch (BYU MATRIX Lab), 2026: 
# Adapted from the CopperMT/pipeline/main_smt_full.sh file of the CopperMT repository
# to run only prediction with an SMT model.
#
# This file is licensed under the GNU General Public License v3.0.
# See CopperMT/CopperMTfiles/LICENSE for the full text.

source $1
export WK_DIR INPUTS_DIR MOSES_DIR DATA_NAME lang

TEXT=$2
OUT=$3
seed=$4

HYP=${OUT}.hyp.txt
SAVE_N_BEST=${OUT}.10_best.txt

DATA_DIR="${INPUTS_DIR}/split_data/${DATA_NAME}"  # Where the data will be saved
WORK_DIR="${WK_DIR}/reference_models/statistical"  # Where the models will be saved

for lang_pair in $(echo ${lang} | tr "," "\n"); do
    echo "RUNNING model_inference.sh for $lang_pair"
    IFS="-" read l_in l_out <<< "${lang_pair}";
    bash statistical_translation/model_inference.sh \
        -i "${l_in}" -o "${l_out}" \
        -m "${MOSES_DIR}" -w "${WORK_DIR}/${seed}" \
        -n 10 \
        -t ${TEXT} \
        -h ${HYP} \
        -b ${SAVE_N_BEST}
    echo ""
done

