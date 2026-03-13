#!/bin/bash

DATA_BIN="data-bin";
CP="checkpoints";

while getopts w:l:fn:b:r:d:u:s:p: o
do  case "$o" in
	l)	LANGS="$OPTARG"; LANGS=$(echo ${LANGS} | tr "," "\n");;
    r)  REF_MODEL_LANGS="$OPTARG";;
    u)  USR_DIR="$OPTARG";;
    w)  WORK_DIR="$OPTARG";;
    d)  DATA_DIR="$OPTARG";;
    f)  DATA_BIN="data-bin-finetune"; CP="checkpoints-finetune";;
    n)  nbest="$OPTARG";;
    b)  beam="$OPTARG";;
    s)  selected_checkpoint="$OPTARG";;
    p)  predict_type="$OPTARG";;
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

GEN_SUBSET='test'
if [ $predict_type = 'test' ]
then
    predict_type='test_on_val'
    GEN_SUBSET='valid'
fi

if [[ ${WORK_DIR} == "" ]]; then
    exit 1;
fi

mkdir -p ${WORK_DIR}/bleu
mkdir -p ${WORK_DIR}/results

echo inference.sh DATA_DIR: $DATA_DIR
echo inference.sh DATA_BIN: $DATA_BIN
echo inference.sh USR_DIR: $USR_DIR

echo "inference.sh nbest: ${nbest}"
echo "inference.sh beam: ${beam}"

for lang_pair in ${LANGS}; do
    echo "NOW RUNNING INFERENCE FOR CHECKPOINT ${selected_checkpoint}"
    echo "IFS='-' read l_in l_out <<< '${lang_pair}';"
    echo "fairseq-generate ${DATA_DIR}/${DATA_BIN}/"
    echo "--gen-subset $GEN_SUBSET"
    echo "--user-dir ${USR_DIR} --path '${selected_checkpoint}'"
    echo "--batch-size 10000 --beam ${beam} --nbest ${nbest}"
    echo "--task 'multilingual_translation' --lang-pairs ${REF_MODEL_LANGS}"
    echo "--results-path '${WORK_DIR}/results/${predict_type}_selected_checkpoint_${l_in}_${l_out}.${l_out}'"
    echo "--scoring sacrebleu -s ${l_in} -t ${l_out}"
    
    # predict
    IFS="-" read l_in l_out <<< "${lang_pair}";
    fairseq-generate ${DATA_DIR}/${DATA_BIN}/ \
    --gen-subset $GEN_SUBSET \
    --user-dir ${USR_DIR} --path "${selected_checkpoint}" \
    --batch-size 10000 --beam ${beam} --nbest ${nbest} \
    --task "multilingual_translation" --lang-pairs ${REF_MODEL_LANGS} \
    --results-path "${WORK_DIR}/results/${predict_type}_selected_checkpoint_${l_in}_${l_out}.${l_out}" \
    --scoring sacrebleu -s ${l_in} -t ${l_out}
    echo "DONE"
    echo ""
done
