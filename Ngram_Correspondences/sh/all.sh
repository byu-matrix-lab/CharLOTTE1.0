source .env

mkdir -p Ngram_Correspondences/entropy_distributions
mkdir -p Ngram_Correspondences/filtered
mkdir -p Ngram_Correspondences/filtered_applied_counts
mkdir -p Ngram_Correspondences/raw
mkdir -p Ngram_Correspondences/samples
mkdir -p Ngram_Correspondences/entropies

cd Ngram_Correspondences

python ngram_correspondences.py -l es-an -p $DATA_HOME/CopperMT/ES-AN-RNN-0_RNN-213_S-0/workspace/reference_models/bilingual/rnn_es-an/0/results/inference_selected_checkpoint_es_an.an/generate-test.txt -c counts/es-en.train.es.txt.ES-AN-RNN-0-RNN-213.counts.txt -m
python ngram_correspondences.py -l fr-mfe -p $DATA_HOME/CopperMT/FR-MFE-RNN-0_RNN-102_S-0/workspace/reference_models/bilingual/rnn_fr-mfe/0/results/inference_selected_checkpoint_fr_mfe.mfe/generate-test.txt -c counts/fr-en.train.fr.txt.FR-MFE-RNN-0-RNN-102.counts.txt -m
python ngram_correspondences.py -l fr-oc -p $DATA_HOME/CopperMT/FR-OC-RNN-0_RNN-251_S-0/workspace/reference_models/bilingual/rnn_fr-oc/0/results/inference_selected_checkpoint_fr_oc.oc/generate-test.txt -c counts/fr-en.train.fr.txt.FR-OC-RNN-0-RNN-251.counts.txt -m
python ngram_correspondences.py -l uz-kaa -p $DATA_HOME/CopperMT/UZ-KAA-RNN-0_RNN-264_S-0/workspace/reference_models/bilingual/rnn_uz-kaa/0/results/inference_selected_checkpoint_uz_kaa.kaa/generate-test.txt -c counts/uz-en.train.uz.txt.UZ-KAA-RNN-0-RNN-264.counts.txt -m

# compile results
python ngram_correspondences.py -r -d $DATA_HOME