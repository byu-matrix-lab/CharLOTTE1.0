# MUST RUN download_data.sh BEFORE THIS!
set -e
source .env
conda activate char1.0

[ -z "$DATA_HOME" ] && echo "ERROR: DATA_HOME not set" && exit 1     

raw_data=${DATA_HOME}/data/raw
opensub=$raw_data/OpenSubtitles
wikimat=$raw_data/WikiMatrix
ccmat=$raw_data/CCMatrix
nllb=$raw_data/nllb
kreyolmt=$raw_data/Kreyol-MT


data_folders=()

data_folders+=("$opensub/es_an")
data_folders+=("$wikimat/es_an")
data_folders+=("$opensub/an_en")
data_folders+=("$wikimat/an_en")
data_folders+=("$ccmat/es_en")

data_folders+=("$ccmat/fr_en")

data_folders+=("$nllb/fr_oc")
data_folders+=("$nllb/oc_en")

cd data/data-cleaning-pipeline
for folder in "${data_folders[@]}"; do
    echo "####################### cleaning $folder #######################"
    echo "pipeline.py -p 8 -d -v -s $folder"
    python pipeline.py -p 8 -d -v -s $folder
    echo ""
    echo ""
done

cd ../..
echo "ALL DATASETS CLEANED"


echo ""
echo ""
echo "Truncating es_en and fr_en to 10M sentence pairs:"

ccmat_files=("$ccmat/es_en/cleaned/src.txt" "$ccmat/es_en/cleaned/tgt.txt" "$ccmat/fr_en/cleaned/src.txt" "$ccmat/fr_en/cleaned/tgt.txt")
for f in "${ccmat_files[@]}"; do
    echo "   truncating $f"
    head -n 10000000 $f > $f.temp
    rm $f
    mv $f.temp $f
done
echo "FINISHED TRUNCATING"
