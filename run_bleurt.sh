#!/usr/bin/env bash
set -euo pipefail

source .env

echo $DATA_HOME
cd bleurt

BASE_DIR="$DATA_HOME/CognateMT/PredictCognates"
OUTPUT_FILE="bleurt_results_with_significance.txt"
RAW_FILE=$(mktemp)
SCORE_DIR=$(mktemp -d) # Temp directory to store sentence-level scores for AR test

# Ensure cleanup of the temporary directory on exit
trap 'rm -rf "$SCORE_DIR" "$RAW_FILE"' EXIT

for lang_pair_dir in "$BASE_DIR"/*/; do
    lang_pair=$(basename "$lang_pair_dir")

    for model_dir in "$lang_pair_dir"*/; do
        model_name=$(basename "$model_dir")

        # Skip REVERSE models
        [[ "$model_name" == *REVERSE* ]] && continue

        # Skip cognate variants (cognate, cognate2, etc.)
        [[ "$model_name" == *cognate* ]] && continue

        json_file="${model_dir}predictions/all_scores.json"
        if [[ ! -f "$json_file" ]]; then
            echo "WARN: no all_scores.json for $model_name" >&2
            continue
        fi

        checkpoint=$(jq -r '.BEST_VAL_BLEU_CHECKPOINT.checkpoint' "$json_file")
        ref_csv=$(jq -r '.TEST_DATA' "$json_file")
        ckpt_dirname=$(basename "$checkpoint")

        if [[ ! -f "$ref_csv" ]]; then
            echo "WARN: missing reference CSV for $model_name ($ref_csv)" >&2
            continue
        fi

        # Extract tgt_path column from row 2 of the CSV, then expand ${DATA_HOME} etc.
        tgt_path_raw=$(awk -F',' '
            NR==1 {
                for (i=1; i<=NF; i++) {
                    h=$i; gsub(/\r/,"",h); gsub(/^[ \t]+|[ \t]+$/,"",h)
                    if (h=="tgt_path") col=i
                }
            }
            NR==2 {
                v=$col; gsub(/\r/,"",v); gsub(/^[ \t]+|[ \t]+$/,"",v); print v
            }' "$ref_csv")

        if [[ -z "$tgt_path_raw" ]]; then
            echo "WARN: could not find tgt_path column for $model_name in $ref_csv" >&2
            continue
        fi

        ref_f=$(eval echo "$tgt_path_raw")
        pred_f="${model_dir}predictions/${ckpt_dirname}/test_predictions.txt"

        if [[ ! -f "$pred_f" ]]; then
            echo "WARN: missing predictions for $model_name ($pred_f)" >&2
            continue
        fi
        if [[ ! -f "$ref_f" ]]; then
            echo "WARN: missing reference for $model_name ($ref_f)" >&2
            continue
        fi

        echo "$pred_f"
        echo "$ref_f"
        scores_file="$SCORE_DIR/${lang_pair}_${model_name}.scores"

        python -m bleurt.score_files \
            -candidate_file="$pred_f" \
            -reference_file="$ref_f" \
            -bleurt_checkpoint=BLEURT-20 \
            -scores_file="$scores_file"

        avg_score=$(awk '{s+=$1; n++} END{if(n>0) printf "%.6f", s/n; else print "NA"}' "$scores_file")

        # Determine method category: NMT, FINETUNE, PRETRAIN, FINETUNE.SC, PRETRAIN.SC
        prefix="${model_name%%.*}"
        rest="${model_name#*.}"
        if [[ "$rest" == SC_* ]]; then
            category="${prefix}.SC"
        else
            category="$prefix"
        fi

        # Save a symlink or copy to a predictable category-based name for the AR test
        ln -sf "$scores_file" "$SCORE_DIR/${lang_pair}_${category}.scores"

        printf '%s\t%s\t%s\t%s\n' "$lang_pair" "$category" "$model_name" "$avg_score" >> "$RAW_FILE"
    done

    # Run Paired Approximate Randomization Test if both models exist
    ft_scores="$SCORE_DIR/${lang_pair}_FINETUNE.scores"
    ft_sc_scores="$SCORE_DIR/${lang_pair}_FINETUNE.SC.scores"

    if [[ -f "$ft_scores" && -f "$ft_sc_scores" ]]; then
        echo "Running significance test for $lang_pair..."
        
        # 1. Capture full output and change newlines into literal '\n' characters
        p_val_output=$(python paired_ar_significance.py "$ft_scores" "$ft_sc_scores" --n-trials 10000 | awk '{printf "%s\\n", $0}')
        
        printf '%s\t%s\t%s\t%s\n' "$lang_pair" "SIGNIFICANCE" "FT_vs_FT.SC" "$p_val_output" >> "$RAW_FILE"
    fi
done

# Organize into: language pair -> method category (fixed order) -> model results
awk -F'\t' '
BEGIN {
    n_cats = split("NMT,FINETUNE,FINETUNE.SC,PRETRAIN,PRETRAIN.SC", cat_order, ",")
}
{
    lang = $1; cat = $2; model = $3; score = $4
    if (!(lang in seen_lang)) { lang_list[++n_lang] = lang; seen_lang[lang] = 1 }
    
    if (cat == "SIGNIFICANCE") {
        sig[lang] = score
    } else {
        count[lang, cat]++
        scores[lang, cat, count[lang, cat]] = score
    }
}
END {
    for (l = 1; l <= n_lang; l++) {
        lang = lang_list[l]
        print "=== " lang " ==="
        for (c = 1; c <= n_cats; c++) {
            cat = cat_order[c]
            n_models = count[lang, cat]
            
            for (i = 1; i <= n_models; i++) {
                printf "%s\t%s\n", cat, scores[lang, cat, i]
            }
        }
        if (lang in sig) {
            # 2. Convert the literal '\n' back into actual newlines for printing
            gsub(/\\n/, "\n", sig[lang])
            printf "%s", sig[lang]
        }
    }
}
' "$RAW_FILE" > "$OUTPUT_FILE"