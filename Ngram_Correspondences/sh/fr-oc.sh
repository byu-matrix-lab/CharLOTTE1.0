source .env

mkdir -p Ngram_Correspondences/entropy_distributions
mkdir -p Ngram_Correspondences/filtered
mkdir -p Ngram_Correspondences/filtered_applied_counts
mkdir -p Ngram_Correspondences/raw
mkdir -p Ngram_Correspondences/samples
mkdir -p Ngram_Correspondences/mappings
mkdir -p Ngram_Correspondences/entropies

cd Ngram_Correspondences

python ngram_correspondences.py -l fr-oc -p $DATA_HOME/CopperMT/FR-OC-RNN-0_RNN-251_S-0/workspace/reference_models/bilingual/rnn_fr-oc/0/results/inference_selected_checkpoint_fr_oc.oc/generate-test.txt -c counts/fr-en.train.fr.txt.FR-OC-RNN-0-RNN-251.counts.txt -m

# compile results
python ngram_correspondences.py -r -d $DATA_HOME
