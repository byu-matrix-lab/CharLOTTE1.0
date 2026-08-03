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
oldi=$raw_data/OLDI


data_folders=()

data_folders+=("$opensub/es_an")
data_folders+=("$wikimat/es_an")
data_folders+=("$opensub/an_en")
data_folders+=("$wikimat/an_en")
data_folders+=("$ccmat/es_en")

data_folders+=("$ccmat/fr_en")

data_folders+=("$nllb/fr_oc")
data_folders+=("$nllb/oc_en")
data_folders+=("$nllb/uz_en")

cd data/data-cleaning-pipeline
for folder in "${data_folders[@]}"; do
    echo "####################### cleaning $folder #######################"
    echo "pipeline.py -p 8 -d -v -s $folder"
    python pipeline.py -p 8 -d -v -s $folder
    echo ""
    echo ""
done

# oldi (moses format)
uz_kaa_folder="$oldi/uz_kaa"
kaa_en_folder="$oldi/kaa_en"
echo "####################### cleaning $uz_kaa_folder #######################"
python pipeline.py -t $uz_kaa_folder -srclang uz -tgtlang kaa -srcpath "$uz_kaa_folder/uz.txt" -tgtpath "$uz_kaa_folder/kaa.txt"

echo "####################### cleaning $kaa_en_folder #######################"
python pipeline.py -t $kaa_en_folder -srclang kaa -tgtlang en -srcpath "$kaa_en_folder/kaa.txt" -tgtpath "$kaa_en_folder/en.txt"

echo ""
echo ""

cd ../..
echo "ALL DATASETS CLEANED"


echo ""
echo ""
echo "Truncating es_en, fr_en, and uz_kaa to 10M sentence pairs:"

trunc_files=("$ccmat/es_en/cleaned/src.txt" "$ccmat/es_en/cleaned/tgt.txt" "$ccmat/fr_en/cleaned/src.txt" "$ccmat/fr_en/cleaned/tgt.txt" "$nllb/uz_en/cleaned/src.txt" "$nllb/uz_en/cleaned/tgt.txt")
for f in "${trunc_files[@]}"; do
    echo "   truncating $f"
    head -n 10000000 $f > $f.temp
    rm $f
    mv $f.temp $f
done

echo "FINISHED TRUNCATING"
