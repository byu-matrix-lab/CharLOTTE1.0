#!/bin/bash
# THIS MUST BE RUN ONLY AFTER clean_data_sbatch.sh/clean_data.sh!!!!
# This will dedupe the training set and ensure no overlap between train / dev / test

source .env
[ -z "$DATA_HOME" ] && echo "ERROR: DATA_HOME not set" && exit 1     

raw_data=${DATA_HOME}/data/raw
DATA_DIR=${DATA_HOME}/data/CharLOTTE_data

flores=$raw_data/flores+
opensub=$raw_data/OpenSubtitles
wikimat=$raw_data/WikiMatrix
ccmat=$raw_data/CCMatrix
nllb=$raw_data/nllb
kreyolmt=$raw_data/Kreyol-MT

an_flores=arg_Latn_arag1245
en_flores=eng_Latn_stan1293
es_flores=spa_Latn_amer1254
fr_flores=fra_Latn_stan1290
oc_flores=oci_Latn_occi1239


################# es/an --> en #################
echo ""
echo ""
echo "################# es/an --> en #################"
# es --> en
python -m data.make_training_data \
    --src_train $ccmat/es_en/cleaned/tgt.txt \
    --tgt_train $ccmat/es_en/cleaned/src.txt \
    --src_val $flores/dev/$es_flores.dev \
    --tgt_val $flores/dev/$en_flores.dev \
    --src_test $flores/devtest/$es_flores.devtest \
    --tgt_test $flores/devtest/$en_flores.devtest \
    --src_lang es \
    --tgt_lang en \
    --out_dir $DATA_DIR

# an --> en
python -m data.make_training_data \
    --src_train $opensub/an_en/cleaned/src.txt,$wikimat/an_en/cleaned/src.txt \
    --tgt_train $opensub/an_en/cleaned/tgt.txt,$wikimat/an_en/cleaned/tgt.txt \
    --src_val $flores/dev/$an_flores.dev \
    --tgt_val $flores/dev/$en_flores.dev \
    --src_test $flores/devtest/$an_flores.devtest \
    --tgt_test $flores/devtest/$en_flores.devtest \
    --src_lang an \
    --tgt_lang en \
    --out_dir $DATA_DIR

# es/an
python -m data.make_training_data \
    --src_train $opensub/es_an/cleaned/tgt.txt,$wikimat/es_an/cleaned/tgt.txt \
    --tgt_train $opensub/es_an/cleaned/src.txt,$wikimat/es_an/cleaned/src.txt \
    --src_val $flores/dev/$es_flores.dev \
    --tgt_val $flores/dev/$an_flores.dev \
    --src_test $flores/devtest/$es_flores.devtest \
    --tgt_test $flores/devtest/$an_flores.devtest \
    --src_lang es \
    --tgt_lang an \
    --out_dir $DATA_DIR

################# fr/mfe --> en #################
echo ""
echo ""
echo "################# fr/mfe --> en #################"
# fr --> en
python -m data.make_training_data \
    --src_train $ccmat/fr_en/cleaned/tgt.txt \
    --tgt_train $ccmat/fr_en/cleaned/src.txt \
    --src_val $flores/dev/$fr_flores.dev \
    --tgt_val $flores/dev/$en_flores.dev \
    --src_test $flores/devtest/$fr_flores.devtest \
    --tgt_test $flores/devtest/$en_flores.devtest \
    --src_lang fr \
    --tgt_lang en \
    --out_dir $DATA_DIR

# mfe --> en
python -m data.make_training_data \
    --src_train $kreyolmt/mfe-eng/train.mfe-eng.mfe \
    --tgt_train $kreyolmt/mfe-eng/train.mfe-eng.eng \
    --src_val $kreyolmt/mfe-eng/val.mfe-eng.mfe \
    --tgt_val $kreyolmt/mfe-eng/val.mfe-eng.eng \
    --src_test $kreyolmt/mfe-eng/test.mfe-eng.mfe \
    --tgt_test $kreyolmt/mfe-eng/test.mfe-eng.eng \
    --src_lang mfe \
    --tgt_lang en \
    --out_dir $DATA_DIR

# fr/mfe
python -m data.make_training_data \
    --src_train $kreyolmt/mfe-fra/train.mfe-fra.fra \
    --tgt_train $kreyolmt/mfe-fra/train.mfe-fra.mfe \
    --src_val $kreyolmt/mfe-fra/val.mfe-fra.fra \
    --tgt_val $kreyolmt/mfe-fra/val.mfe-fra.mfe \
    --src_test $kreyolmt/mfe-fra/test.mfe-fra.fra \
    --tgt_test $kreyolmt/mfe-fra/test.mfe-fra.mfe \
    --src_lang fr \
    --tgt_lang mfe \
    --out_dir $DATA_DIR

################# fr/oc --> en #################
echo ""
echo ""
echo "################# fr/oc --> en #################"
# fr --> en
# Already done ^^

# oc --> en
python -m data.make_training_data \
    --src_train $nllb/oc_en/cleaned/tgt.txt \
    --tgt_train $nllb/oc_en/cleaned/src.txt \
    --src_val $flores/dev/$oc_flores.dev \
    --tgt_val $flores/dev/$en_flores.dev \
    --src_test $flores/devtest/$oc_flores.devtest \
    --tgt_test $flores/devtest/$en_flores.devtest \
    --src_lang oc \
    --tgt_lang en \
    --out_dir $DATA_DIR

# fr/oc
python -m data.make_training_data \
    --src_train $nllb/fr_oc/cleaned/src.txt \
    --tgt_train $nllb/fr_oc/cleaned/tgt.txt \
    --src_val $flores/dev/$fr_flores.dev \
    --tgt_val $flores/dev/$oc_flores.dev \
    --src_test $flores/devtest/$fr_flores.devtest \
    --tgt_test $flores/devtest/$oc_flores.devtest \
    --src_lang fr \
    --tgt_lang oc \
    --out_dir $DATA_DIR

