source .env

mkdir -p Ngram_Correspondences/entropy_distributions
mkdir -p Ngram_Correspondences/filtered
mkdir -p Ngram_Correspondences/filtered_applied_counts
mkdir -p Ngram_Correspondences/raw
mkdir -p Ngram_Correspondences/samples
mkdir -p Ngram_Correspondences/mappings
mkdir -p Ngram_Correspondences/entropies

cd Ngram_Correspondences

python ngram_correspondences.py -l fr-mfe -p $DATA_HOME/CopperMT/FR-MFE-RNN-0_RNN-102_S-0/workspace/reference_models/bilingual/rnn_fr-mfe/0/results/inference_selected_checkpoint_fr_mfe.mfe/generate-test.txt -c counts/fr-en.train.fr.txt.FR-MFE-RNN-0-RNN-102.counts.txt -m

# compile results
python ngram_correspondences.py -r -d $DATA_HOME
