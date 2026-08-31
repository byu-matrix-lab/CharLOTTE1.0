source .env

mkdir -p Ngram_Correspondences/entropy_distributions
mkdir -p Ngram_Correspondences/filtered
mkdir -p Ngram_Correspondences/filtered_applied_counts
mkdir -p Ngram_Correspondences/raw
mkdir -p Ngram_Correspondences/samples
mkdir -p Ngram_Correspondences/mappings
mkdir -p Ngram_Correspondences/entropies

cd Ngram_Correspondences

python ngram_correspondences.py -l uz-kaa -p $DATA_HOME/CopperMT/UZ-KAA-RNN-0_RNN-264_S-0/workspace/reference_models/bilingual/rnn_uz-kaa/0/results/inference_selected_checkpoint_uz_kaa.kaa/generate-test.txt -c counts/uz-en.train.uz.txt.UZ-KAA-RNN-0-RNN-264.counts.txt -m

# compile results
python ngram_correspondences.py -r -d $DATA_HOME
