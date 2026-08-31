source .env

mkdir -p Ngram_Correspondences/entropy_distributions
mkdir -p Ngram_Correspondences/filtered
mkdir -p Ngram_Correspondences/filtered_applied_counts
mkdir -p Ngram_Correspondences/raw
mkdir -p Ngram_Correspondences/samples
mkdir -p Ngram_Correspondences/mappings
mkdir -p Ngram_Correspondences/entropies

cd Ngram_Correspondences

python ngram_correspondences.py -l es-an -p $DATA_HOME/CopperMT/ES-AN-RNN-0_RNN-213_S-0/workspace/reference_models/bilingual/rnn_es-an/0/results/inference_selected_checkpoint_es_an.an/generate-test.txt -c counts/es-en.train.es.txt.ES-AN-RNN-0-RNN-213.counts.txt -m

# compile results
python ngram_correspondences.py -r -d $DATA_HOME
