#!/bin/bash

# Original work: CopperMT (https://github.com/clefourrier/CopperMT)
# by Clémentine Fourrier (clefourrier), licensed under GNU GPL 3.
#
# Modified by Brendan Hatch (BYU MATRIX Lab), 2026: 
# This script is derived from the file CopperMT/pipeline/statistical_translation/model_test_nbest.sh 
# of the CopperMT repository, adapted for running model inference.
#
# This file is licensed under the GNU General Public License v3.0.
# See CopperMT/CopperMTfiles/LICENSE for the full text.

while getopts n:m:w:d:i:o:t:h:b:r: o
do  case "$o" in
	m)	MOSES_DIR="$OPTARG";;
    d)  DATA_DIR="$OPTARG";;
    w)  WORK_DIR="$OPTARG";;
    i)  l_in="$OPTARG";;
    o)  l_out="$OPTARG";;
    n)  n_best="$OPTARG";;
    t)  text="$OPTARG";;
    h)  hyp="$OPTARG";;
    b)  save_n_best="$OPTARG";;
    r)  save_results="$OPTARG";;
    [?])	print >&2 "Usage: $0 [-i source language (input language)]
                                 [-o target language (output language)]
                                 [-w working directory]
                                 [-d data directory]
                                 [-m path to moses]
                                 [-n n_best value]
                                 [-t text to run inference on]
                                 [-h where to save hypothesis]
                                 [-b where to save n-best]
                                 "
		exit 1;;
	esac
done

echo "nohup nice ${MOSES_DIR}/mosesdecoder/bin/moses \
     -f ${WORK_DIR}/${l_in}_${l_out}/train/model/moses.ini \
     -n-best-list ${save_n_best} \
     ${n_best} distinct < ${text} \
     > ${hyp}"

nohup nice ${MOSES_DIR}/mosesdecoder/bin/moses \
     -f ${WORK_DIR}/${l_in}_${l_out}/train/model/moses.ini \
     -n-best-list ${save_n_best} \
     ${n_best} distinct < ${text} \
     > ${hyp}
