#!/bin/bash

DATA_BIN="data-bin";
CP="checkpoints"
while getopts w:l:fn:b:r:d:u: o
do  case "$o" in
	l)	LANGS="$OPTARG"; LANGS=$(echo ${LANGS} | tr "," "\n");;
    r)  REF_MODEL_LANGS="$OPTARG";;
    u)  USR_DIR="$OPTARG";;
    w)  WORK_DIR="$OPTARG";;
    d)  DATA_DIR="$OPTARG";;
    f)  DATA_BIN="data-bin-finetune"; CP="checkpoints-finetune";;
    n)  nbest="$OPTARG";;
    b)  beam="$OPTARG";;
    [?])	print >&2 "Usage: $0 [-l lang pairs of interest (format l_in-l_out,l_in2-l_out2...)]
                                 [-r all model lang pairs (same format)]
                                 [-u user directory - path to multilingual_rnns]
                                 [-w working directory]
                                 [-d data directory]
                                 [-f (we are looking at fine-tuned data/models)]
                                 [-n nbest dimension]
                                 [-b beam dimension]
                                 "
		exit 1;;
	esac
done

if [[ ${WORK_DIR} == "" ]]; then
    exit 1;
fi
echo "--------- SELECTING BEST CHECKPOINT"

mkdir -p "${WORK_DIR}/bleu"
# Reinit file
echo "" > "${WORK_DIR}/bleu/all_bleu.csv"

echo "Generating data from ${DATA_DIR}/${DATA_BIN}/"

# Generate all bests and save to file
for f in $(ls "${WORK_DIR}/${CP}/$EXP_NAME"); do
    for lang_pair in ${LANGS}; do
        echo "GENERATING FOR CHECKPOINT"
        echo "$f, $lang_pair"
        echo "IFS='-' read l_in l_out <<< '${lang_pair}';"
        echo "bleu=\$(fairseq-generate ${DATA_DIR}/${DATA_BIN}/"
        echo "--gen-subset 'valid'"
        echo "--user-dir ${USR_DIR} --path '${WORK_DIR}/${CP}/${f}'"
        echo "--batch-size 10000 --beam ${beam} --nbest ${nbest}"
        echo "--task 'multilingual_translation' --lang-pairs ${REF_MODEL_LANGS}"
        echo "--scoring sacrebleu -s ${l_in} -t ${l_out} \| tail -n1 \|"

        IFS="-" read l_in l_out <<< "${lang_pair}";
        bleu=$(fairseq-generate ${DATA_DIR}/${DATA_BIN}/ \
        --gen-subset "valid" \
        --user-dir ${USR_DIR} --path "${WORK_DIR}/${CP}/${f}" \
        --batch-size 10000 --beam ${beam} --nbest ${nbest} \
        --task "multilingual_translation" --lang-pairs ${REF_MODEL_LANGS} \
        --scoring sacrebleu -s ${l_in} -t ${l_out} | tail -n1 | \
        awk -F 'BLEU = ' '{print $2"\n"}'  | \
        awk -F ' ' '{printf $1"\n"}' | awk 'NF > 0')

        echo "${f} ${l_in} ${l_out} ${bleu}" >> "${WORK_DIR}/bleu/all_bleu.csv"
        echo ""
    done
done

# Select and save the best checkpoint
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
python ${DIR}/checkpoint_select_best_from_file.py "${WORK_DIR}" "${CP}"