#!/bin/bash

source $1
export WK_DIR INPUTS_DIR DATA_NAME lang

seed=$2
nbest=$3
beam=$4


echo "########## main_nmt_bilingual_full_CharLOTTE.sh ##########"
echo "WK_DIR ${WK_DIR}"
echo "INPUTS_DIR ${INPUTS_DIR}"
echo "DATA_NAME ${DATA_NAME}"
echo "lang ${lang}"
echo "seed" "${seed}"
echo "nbest" "${nbest}"
echo "beam" "${beam}"
echo "--------------------------------------------------------"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
USER_DIR="${DIR}/neural_translation/multilingual_rnns"  # Link to "multilingual_rnns"

# ------ PARAMETERS
# INPUTS
ORIGIN_DATA_DIR="${INPUTS_DIR}/split_data/${DATA_NAME}"  # Link to the original data files
PARAMETER_DIR="${INPUTS_DIR}/parameters/bilingual_default"  # Contains the parameter files
# WORKING
DATA_DIR="${WK_DIR}/reference_models/bilingual/data"  # Where the data will be saved
WORK_DIR="${WK_DIR}/reference_models/bilingual"  # Where the models will be saved
mkdir -p "${WK_DIR}/reference_models/bilingual"
echo "${ORIGIN_DATA_DIR} ${PARAMETER_DIR} ${DATA_DIR} ${WORK_DIR}"

# ------ PREPROCESSING
bash "${DIR}/neural_translation/data_preprocess.sh" \
    -l $lang \
    -o "${ORIGIN_DATA_DIR}/${seed}"\
    -d "${DATA_DIR}/${seed}"
# done

# ------- TRAINING RNN AND TRANSFORMER
for lang_pairs in $lang; do
    for model in "rnn"; do
        bash "${DIR}/neural_translation/model_train.sh"  -l ${lang_pairs} \
            -d "${DATA_DIR}/${seed}" \
            -w "${WORK_DIR}/${model}_${lang_pairs}/${seed}" \
            -p "${PARAMETER_DIR}/default_parameters_${model}_${lang_pairs}.txt" \
            -u "${USER_DIR}" -e 20

        bash "${DIR}/neural_translation/checkpoint_select_best.sh" \
            -l ${lang_pairs} -r ${lang_pairs} \
            -w "${WORK_DIR}/${model}_${lang_pairs}/${seed}" \
            -d "${DATA_DIR}/${seed}" \
            -u "${USER_DIR}" \
            -n $nbest -b $beam
    done
done
