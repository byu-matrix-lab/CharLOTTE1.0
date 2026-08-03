#!/bin/bash

set -e

source .env

source "$(conda info --base)/etc/profile.d/conda.sh"

echo "Starting pred_SC.sh------------"
date
echo "-------------------------------"

    ###############################################
#-- #                 1) ARGUMENTS                # --#
    ###############################################
echo "    ###############################################"
echo "#-- #                 1) ARGUMENTS                # --#"
echo "    ###############################################"
source $1 # .cfg file from from Pipeline/cfg/SC

echo "Arguments:-"
echo "    MODULE_HOME_DIR=$MODULE_HOME_DIR"
echo ""
echo "    SRC=$SRC"
echo "    TGT=$TGT"
echo "    PARALLEL_TRAIN=$PARALLEL_TRAIN"
echo "    PARALLEL_VAL=$PARALLEL_VAL"
echo "    PARALLEL_TEST=$PARALLEL_TEST"
echo "    APPLY_TO=$APPLY_TO"
echo "    SC_MODEL_TYPE=$SC_MODEL_TYPE"
echo "    SEED=$SEED"
echo "    SC_MODEL_ID=$SC_MODEL_ID"
echo "    COPPERMT_DATA_DIR=$COPPERMT_DATA_DIR"
echo "    COPPERMT_DIR=$COPPERMT_DIR"
echo "    PARAMETERS_DIR=$PARAMETERS_DIR"
echo "    RNN_HYPERPARAMS_ID=$RNN_HYPERPARAMS_ID"
echo "    BEAM=$BEAM"
echo "    NBEST=$NBEST"
echo "    LOG_P_THRESH=$LOG_P_THRESH"
echo "-------------------------------"

    ###############################################
#-- #              2) APPLY SC MODEL              # --#
    ###############################################
echo ""
echo ""
echo ""
echo ""
echo "    ###############################################"
echo "#-- #              2) APPLY SC MODEL              # --#"
echo "    ###############################################"


######## 2.1 Write the CopperMT parameters file ########
echo ""
echo ""
echo "######## 2.1 Write the CopperMT parameters file ########"
PARAMETERS_F="${PARAMETERS_DIR}/parameters.${SC_MODEL_ID}_${SC_MODEL_TYPE}-${RNN_HYPERPARAMS_ID}_S-${SEED}.cfg"
python Pipeline/write_scripts.py \
    --src ${SRC} \
    --tgt ${TGT} \
    --coppermt_data_dir ${COPPERMT_DATA_DIR} \
    --sc_model_type ${SC_MODEL_TYPE} \
    --rnn_hyperparams_id ${RNN_HYPERPARAMS_ID} \
    --seed ${SEED} \
    --parameters $PARAMETERS_F \
    --sc_model_id $SC_MODEL_ID

######## 2.2 Get selected SC model ########
echo ""
echo ""
echo "######## 2.2 Get selected SC model ########"
conda activate cop_mt
echo "    TYPE=$SC_MODEL_TYPE"
if [ $SC_MODEL_TYPE = "RNN" ]
then
    # Get selected model
    WORKSPACE_SEED_DIR=$COPPERMT_DATA_DIR/${SC_MODEL_ID}_${SC_MODEL_TYPE}-${RNN_HYPERPARAMS_ID}_S-${SEED}/workspace/reference_models/bilingual/rnn_${SRC}-${TGT}/${SEED}
    SELECTED_RNN_CHECKPOINT=${WORKSPACE_SEED_DIR}/checkpoints/checkpoint_best.selected.pt

    echo "SELECTED_RNN_CHECKPOINT: `${SELECTED_RNN_CHECKPOINT}`"
fi



######## 2.3 Delete inference directories if pre-existing ########
echo ""
echo ""
echo "######## 2.3 Delete inference directories if pre-existing ########"
INFERENCE_DATA_DIR=${COPPERMT_DATA_DIR}/${SC_MODEL_ID}_${SC_MODEL_TYPE}-${RNN_HYPERPARAMS_ID}_S-${SEED}/workspace/reference_models/bilingual/data/inference
INFERENCE_DIR=${COPPERMT_DATA_DIR}/${SC_MODEL_ID}_${SC_MODEL_TYPE}-${RNN_HYPERPARAMS_ID}_S-${SEED}/workspace/reference_models/bilingual/rnn_${SRC}-${TGT}/${SEED}/results/inference_selected_checkpoint_${SRC}_${TGT}.${SRC}
for directory in $INFERENCE_DATA_DIR $INFERENCE_DIR ; do
    if [ -d $directory ]; then
        echo "    deleting ${directory}"
        rm -r $directory
    fi
done

######## 2.4 APPLY SC ########
echo ""
echo ""
echo "######## 2.4 APPLY SC ########"
cd $MODULE_HOME_DIR
conda activate char1.0
SPLIT_DATA=${COPPERMT_DATA_DIR}/${SC_MODEL_ID}_${SC_MODEL_TYPE}-${RNN_HYPERPARAMS_ID}_S-${SEED}/inputs/split_data/${SRC}_${TGT}/${SEED}
COPPER_MT_PREP_OUT_DIR=${COPPERMT_DATA_DIR}/${SC_MODEL_ID}_${SC_MODEL_TYPE}-${RNN_HYPERPARAMS_ID}_S-${SEED}/inputs/split_data/${SRC}_${TGT}/inference

if [ -d $COPPER_MT_PREP_OUT_DIR ]; then
    echo "deleting ${COPPER_MT_PREP_OUT_DIR}"
    rm -r $COPPER_MT_PREP_OUT_DIR
fi
mkdir $COPPER_MT_PREP_OUT_DIR

if [[ "$PARALLEL_VAL" == *"uz-kaa"* ]]; then
  PARALLEL_FILES=( "$PARALLEL_TRAIN" "$PARALLEL_TEST" )
else
  PARALLEL_FILES=( "$PARALLEL_TRAIN" "$PARALLEL_VAL" "$PARALLEL_TEST" )
fi
IFS="," read -r -a APPLY_TO_FILES <<< $APPLY_TO
ALL_CSV_FILES=( "${PARALLEL_FILES[@]}" "${APPLY_TO_FILES[@]}" )
echo "-- APPLYING SC MODEL TO FILES --"
for f in ${ALL_CSV_FILES[@]} ; do
    if [ $f = "null" ]
    then
        echo "    DATA CSV F is null"
    else
        echo "    DATA CSV F: ${f}"
        echo ""
        # prepare mode
        python NMT/hr_CopperMT.py \
            --data $f \
            --out $COPPER_MT_PREP_OUT_DIR \
            -hr $SRC \
            -lr $TGT \
            --training_data $SPLIT_DATA \
            --limit_lang $SRC

        cd ${COPPERMT_DIR}/pipeline
        if [ $SC_MODEL_TYPE = "RNN" ]
        then
            conda activate cop_mt
            echo "    main_nmt_bilingual_full_CharLOTTE_PREDICT.sh ${PARAMETERS_F} ${SELECTED_RNN_CHECKPOINT} ${SEED} inference ${NBEST} ${BEAM}"
            bash "main_nmt_bilingual_full_CharLOTTE_PREDICT.sh" "${PARAMETERS_F}" "${SELECTED_RNN_CHECKPOINT}" "${SEED}" "inference" "${NBEST}" "${BEAM}"
            COPPERMT_RESULTS=${COPPERMT_DATA_DIR}/${SC_MODEL_ID}_${SC_MODEL_TYPE}-${RNN_HYPERPARAMS_ID}_S-${SEED}/workspace/reference_models/bilingual/rnn_${SRC}-${TGT}/${SEED}/results/inference_selected_checkpoint_${SRC}_${TGT}.${TGT}/generate-test.txt

            conda activate char1.0
            cd $MODULE_HOME_DIR
            python NMT/hr_CopperMT.py \
                --function retrieve \
                --data $f \
                --CopperMT_results $COPPERMT_RESULTS \
                -hr $SRC \
                -lr $TGT \
                --MODEL_ID "${SC_MODEL_ID}-${SC_MODEL_TYPE}-${RNN_HYPERPARAMS_ID}" \
                --log_p_thresh $LOG_P_THRESH
        elif [ $SC_MODEL_TYPE = "SMT" ]
        then
            conda activate cop_mt
            TEXT=$COPPER_MT_PREP_OUT_DIR/test_${SRC}_${TGT}.${SRC}
            HYP_OUT=$COPPER_MT_PREP_OUT_DIR/test_${SRC}_${TGT}.${TGT}
            echo "    main_smt_full_CharLOTTE_PREDICT.sh ${PARAMETERS_F} ${TEXT} ${HYP_OUT} ${SEED}"
            bash "main_smt_full_CharLOTTE_PREDICT.sh" "${PARAMETERS_F}" "${TEXT}" "${HYP_OUT}" "${SEED}"
            
            HYP_OUT_F=$HYP_OUT.hyp.txt
            conda activate char1.0
            cd $MODULE_HOME_DIR
            python NMT/hr_CopperMT.py \
                --function retrieve \
                --data $f \
                --CopperMT_SMT_results ${TEXT},${HYP_OUT_F} \
                -hr $SRC \
                -lr $TGT \
                --MODEL_ID "${SC_MODEL_ID}-${SC_MODEL_TYPE}-${RNN_HYPERPARAMS_ID}" \
                --log_p_thresh $LOG_P_THRESH
        fi
    fi
done


echo "Finished-----------------------"
date
echo "-------------------------------"