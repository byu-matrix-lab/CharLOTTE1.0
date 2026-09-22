#!/bin/bash

set -e

source .env

source "$(conda info --base)/etc/profile.d/conda.sh"

conda activate cop_mt

# fr-oc
python Pipeline/evaluate.py --ref $CHARLOTTE_HOME/Pipeline/true_cognate/data/true_cognates.fr-oc.oc.txt --hyp $CHARLOTTE_HOME/Pipeline/true_cognate/data/true_cognates.fr-oc.fr.SC_FR-OC-RNN-0-RNN-251_fr2oc.txt --out "Pipeline/true_cognate/results/results.fr-oc.txt"
python Pipeline/evaluate.py --ref $CHARLOTTE_HOME/Pipeline/true_cognate/data/true_cognates.fr-oc.oc.txt --hyp $CHARLOTTE_HOME/Pipeline/true_cognate/data/true_cognates.fr-oc.fr.txt --out "Pipeline/true_cognate/results/results.baseline.fr-oc.txt"

# compile the data
dir="Pipeline/true_cognate/results"                      
out="Pipeline/true_cognate/cognate_eval_results.txt"
: > "$out"

for f in "$dir"/results.baseline.*.txt; do
  pair=$(basename "$f" .txt); pair=${pair#results.baseline.}   # e.g. an-es
  g="$dir/results.$pair.txt"
  [ -f "$g" ] || continue
  base=$(grep -m1 '^BLEU_SCORE:' "$f" | awk '{print $2}')
  norm=$(grep -m1 '^BLEU_SCORE:' "$g" | awk '{print $2}')
  echo "$pair: PL: $base -- PL': $norm" >> "$out"
done