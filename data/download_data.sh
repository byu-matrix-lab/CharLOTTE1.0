#!/bin/bash

conda activate char1.0

source .env
[ -z "$DATA_HOME" ] && echo "ERROR: DATA_HOME not set" && exit 1     

raw_data=${DATA_HOME}/data/raw
rm -rf $raw_data
mkdir -p $raw_data

flores=$raw_data/flores+
opensub=$raw_data/OpenSubtitles
wikimat=$raw_data/WikiMatrix
ccmat=$raw_data/CCMatrix
nllb=$raw_data/nllb
kreyolmt=$raw_data/Kreyol-MT
oldi=$raw_data/OLDI
mkdir $flores
mkdir $opensub
mkdir $wikimat
mkdir $ccmat
mkdir $nllb
mkdir $kreyolmt
mkdir $oldi

########################## FLORES+ ##########################
an_flores=arg_Latn_arag1245
en_flores=eng_Latn_stan1293
es_flores=spa_Latn_amer1254
fr_flores=fra_Latn_stan1290
oc_flores=oci_Latn_occi1239

python data/download_flores_plus.py \
    --out_dir $flores \
    --auth_token $HF_TOKEN \
    --langs $an_flores,$en_flores,$es_flores,$fr_flores,$oc_flores

en_flores_dev_path=$raw_data/dev/$en_flores.dev
en_flores_devtest_path=$raw_data/devtest/$en_flores.devtest

es_flores_dev_path=$raw_data/dev/$es_flores.dev
es_flores_devtest_path=$raw_data/devtest/$es_flores.devtest

fr_flores_dev_path=$raw_data/dev/$fr_flores.dev
fr_flores_devtest_path=$raw_data/devtest/$fr_flores.devtest

oc_flores_dev_path=$raw_data/dev/$oc_flores.dev
oc_flores_devtest_path=$raw_data/devtest/$oc_flores.devtest


########################## es/an --> en ##########################

# es/an
es_an_opensub=$opensub/es_an
mkdir $es_an_opensub
wget -P $es_an_opensub https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/tmx/an-es.tmx.gz
es_an_opensub_tmx=$es_an_opensub/an-es.tmx.gz
gunzip $es_an_opensub_tmx

es_an_wikimat=$wikimat/es_an
mkdir $es_an_wikimat
wget -P $es_an_wikimat https://object.pouta.csc.fi/OPUS-WikiMatrix/v1/tmx/an-es.tmx.gz
es_an_wikimat_tmx=$es_an_wikimat/an-es.tmx.gz
gunzip $es_an_wikimat_tmx

# an --> en
an_en_opensub=$opensub/an_en
mkdir $an_en_opensub
wget -P $an_en_opensub https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/tmx/an-en.tmx.gz
an_en_opensub_tmx=$an_en_opensub/an-en.tmx.gz
gunzip $an_en_opensub_tmx

an_en_wikimat=$wikimat/an_en
mkdir $an_en_wikimat
wget -P $an_en_wikimat https://object.pouta.csc.fi/OPUS-WikiMatrix/v1/tmx/an-en.tmx.gz
an_en_wikimat_tmx=$an_en_wikimat/an-en.tmx.gz
gunzip $an_en_wikimat_tmx

# es --> en
es_en_ccmat=$ccmat/es_en
mkdir $es_en_ccmat
wget -O - https://object.pouta.csc.fi/OPUS-CCMatrix/v1/tmx/en-es.tmx.gz | gunzip | head -c 9600M > $es_en_ccmat/en-es.tmx
# Truncate to line 119,782,829
head -n 119782829 $es_en_ccmat/en-es.tmx > $es_en_ccmat/en-es.tmx.trunc
rm $es_en_ccmat/en-es.tmx
mv $es_en_ccmat/en-es.tmx.trunc $es_en_ccmat/en-es.tmx
# Fix the bottom
last_tu=$(grep -an "</tu>" $es_en_ccmat/en-es.tmx | tail -1 | cut -d: -f1)
head -n $last_tu $es_en_ccmat/en-es.tmx > $es_en_ccmat/en-es.temp.tmx
rm $es_en_ccmat/en-es.tmx
mv $es_en_ccmat/en-es.temp.tmx $es_en_ccmat/en-es.tmx
printf "\n  </body>\n</tmx>\n" >> $es_en_ccmat/en-es.tmx
es_en_ccmat_tmx=$es_en_ccmat/en-es.tmx




########################## fr/mfe --> en ##########################
# fr/mfe + mfe --> en
Download Kreyol-MT
python data/download_kreyol_mt.py \
    --src mfe \
    --tgt eng,fra \
    --out $kreyolmt

# fr --> en
fr_en_ccmat=$ccmat/fr_en
mkdir $fr_en_ccmat
wget -O - https://object.pouta.csc.fi/OPUS-CCMatrix/v1/tmx/en-fr.tmx.gz | gunzip | head -c 9000M > $fr_en_ccmat/en-fr.tmx
# Truncate it to line 108,998,436
head -n 108998436 $fr_en_ccmat/en-fr.tmx > $fr_en_ccmat/en-fr.tmx.trunc
rm $fr_en_ccmat/en-fr.tmx
mv $fr_en_ccmat/en-fr.tmx.trunc $fr_en_ccmat/en-fr.tmx
# Fix the bottom
last_tu=$(grep -an "</tu>" $fr_en_ccmat/en-fr.tmx | tail -1 | cut -d: -f1)
head -n $last_tu $fr_en_ccmat/en-fr.tmx > $fr_en_ccmat/en-fr.temp.tmx
rm $fr_en_ccmat/en-fr.tmx
mv $fr_en_ccmat/en-fr.temp.tmx $fr_en_ccmat/en-fr.tmx
printf "\n  </body>\n</tmx>\n" >> $fr_en_ccmat/en-fr.tmx
# need to remove bad <tu> containing string 'creationdate' that breaks the cleaning pipeline
head -n 97923559 $fr_en_ccmat/en-fr.tmx > $fr_en_ccmat/en-fr.BEFORE.tmx
total_lines=$(wc -l < $fr_en_ccmat/en-fr.tmx)
tail_n=$((total_lines - 97923562))
tail -n $tail_n $fr_en_ccmat/en-fr.tmx > $fr_en_ccmat/en-fr.AFTER.tmx
rm $fr_en_ccmat/en-fr.tmx
cat $fr_en_ccmat/en-fr.BEFORE.tmx $fr_en_ccmat/en-fr.AFTER.tmx > $fr_en_ccmat/en-fr.tmx
rm $fr_en_ccmat/en-fr.BEFORE.tmx
rm $fr_en_ccmat/en-fr.AFTER.tmx
fr_en_ccmat_tmx=$fr_en_ccmat/en-fr.tmx


########################## fr/oc --> en ##########################

# fr/oc
fr_oc_nllb=$nllb/fr_oc
mkdir $fr_oc_nllb
wget -P $fr_oc_nllb https://object.pouta.csc.fi/OPUS-NLLB/v1/tmx/fr-oc.tmx.gz
fr_oc_nllb_tmx=$fr_oc_nllb/fr-oc.tmx.gz
gunzip $fr_oc_nllb_tmx

# oc --> en
oc_en_nllb=$nllb/oc_en
mkdir $oc_en_nllb
wget -P $oc_en_nllb https://object.pouta.csc.fi/OPUS-NLLB/v1/tmx/en-oc.tmx.gz
oc_en_nllb_tmx=$oc_en_nllb/en-oc.tmx.gz
gunzip $oc_en_nllb_tmx

# fr --> en
# Already got it above ^^




########################## uz/kaa --> en ##########################
uz_en_nllb=$nllb/uz_en
mkdir $uz_en_nllb
wget -O - https://object.pouta.csc.fi/OPUS-NLLB/v1/tmx/en-uz.tmx.gz | gunzip | head -c 3000M > $uz_en_nllb/en-uz.tmx

head -n 54899502 $uz_en_nllb/en-uz.tmx > $uz_en_nllb/en-uz.tmx.trunc
# # Truncate it to line 54899502
rm $uz_en_nllb/en-uz.tmx
mv $uz_en_nllb/en-uz.tmx.trunc $uz_en_nllb/en-uz.tmx
# # Fix the bottom
last_tu=$(grep -an "</tu>" $uz_en_nllb/en-uz.tmx | tail -1 | cut -d: -f1)
head -n $last_tu $uz_en_nllb/en-uz.tmx > $uz_en_nllb/en-uz.temp.tmx
rm $uz_en_nllb/en-uz.tmx
mv $uz_en_nllb/en-uz.temp.tmx $uz_en_nllb/en-uz.tmx
printf "\n  </body>\n</tmx>\n" >> $uz_en_nllb/en-uz.tmx
uz_en_nllb_tmx=$uz_en_nllb/en-uz.tmx

uz_kaa_oldi=$oldi/uz_kaa
kaa_en_oldi=$oldi/kaa_en
mkdir $uz_kaa_oldi
mkdir $kaa_en_oldi

uz_flores=uzn_Latn_nort2690
uz_flores_dev_path=$raw_data/flores+/dev/$uz_flores.dev
uz_flores_devtest_path=$raw_data/flores+/devtest/$uz_flores.devtest

kaa_flores=kaa_Latn_kara1467
kaa_flores_devtest_path=$raw_data/flores+/devtest/$kaa_flores.devtest

python data/download_uz_kaa.py \
    -t $HF_TOKEN \
    --uz_kaa_output $uz_kaa_oldi \
    --kaa_en_output $kaa_en_oldi \
    --uz_dev_output $uz_flores_dev_path \
    --uz_devtest_output $uz_flores_devtest_path \
    --kaa_devtest_output $kaa_flores_devtest_path



echo "ALL DATA DOWNLOADED"