#!/bin/bash

source .env

results_dir=$DATA_HOME/CognateMT/PredictCognates
output="NMT_results.txt" 
> "$output"

declare -A sections
declare -A sections_rev

for lang_pair_dir in $results_dir/*/; do
    lang_pair=$(basename "$lang_pair_dir")

    for experiment_dir in "$lang_pair_dir"*/; do
        experiment=$(basename "$experiment_dir")
        scores_file="$experiment_dir/predictions/all_scores.json"

        if [[ -f "$scores_file" ]]; then
            test_bleu=$(python3 -c "import json; d=json.load(open('$scores_file')); print(d['BEST_VAL_BLEU_CHECKPOINT']['test_BLEU'])")
            test_chrf=$(python3 -c "import json; d=json.load(open('$scores_file')); print(d['BEST_VAL_BLEU_CHECKPOINT']['test_chrF'])")
            line="$lang_pair | test_BLEU: $test_bleu | test_chrF: $test_chrf"

            if [[ "$experiment" == FINETUNE.SC*cognate* ]]; then
                section="cognate_finetune"
            elif [[ "$experiment" == PRETRAIN.SC*cognate* ]]; then
                section="cognate_pretrain"
            elif [[ "$experiment" == FINETUNE.SC* ]]; then
                section="charlotte"
            elif [[ "$experiment" == PRETRAIN.SC* ]]; then
                section="pretrain_charlotte"
            elif [[ "$experiment" == FINETUNE* ]]; then
                section="transfer"
            elif [[ "$experiment" == PRETRAIN* ]]; then
                section="pretrain_transfer"
            elif [[ "$experiment" == NMT* ]]; then
                section="simple"
            else
                section="other"
            fi

            if [[ "$experiment" == *.REVERSE* ]]; then
                reversed_pair=$(echo "$lang_pair" | awk -F'-' '{print $2"-"$1}')
                line="$reversed_pair | test_BLEU: $test_bleu | test_chrF: $test_chrf"
                sections_rev[$section]+="$line"$'\n'
            else
                sections[$section]+="$line"$'\n'
            fi
        fi
    done
done

print_section() {
    local title=$1
    local key=$2
    echo "=== $title ===" >> "$output"
    echo "${sections[$key]}" >> "$output"
}

print_section_rev() {
    local title=$1
    local key=$2
    echo "=== $title ===" >> "$output"
    echo "${sections_rev[$key]}" >> "$output"
}

print_section "Simple" "simple"
print_section "Pretrain for Transfer" "pretrain_transfer"
print_section "Transfer" "transfer"
print_section "Pretrain for CharLOTTE" "pretrain_charlotte"
print_section "CharLOTTE" "charlotte"
print_section "Pretrain for Cognate" "cognate_pretrain"
print_section "Cognate" "cognate_finetune"

echo "" >> "$output"
echo "=== REVERSE ===" >> "$output"
echo "" >> "$output"

print_section_rev "Simple" "simple"
print_section_rev "Pretrain for Transfer" "pretrain_transfer"
print_section_rev "Transfer" "transfer"
print_section_rev "Pretrain for CharLOTTE" "pretrain_charlotte"
print_section_rev "CharLOTTE" "charlotte"

echo "Done. Results written to $output"