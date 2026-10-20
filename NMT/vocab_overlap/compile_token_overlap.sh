#!/bin/bash

set -euo pipefail
 
DIR="NMT/vocab_overlap/results"
OUT="$DIR/vocab_overlap_results_summary.txt"
 
> "$OUT"
 
for jsd_file in "$DIR"/vocab_overlap_*.JSD.json; do
    [ -e "$jsd_file" ] || continue
 
    base=$(basename "$jsd_file")
    pair=${base#vocab_overlap_}
    pair=${pair%.JSD.json}
 
    jacc_file="$DIR/vocab_overlap_${pair}.JACC.json"
 
    jsd_val=$(tr -d '[:space:]' < "$jsd_file")
 
    if [ -e "$jacc_file" ]; then
        jacc_val=$(grep -o '[-0-9.eE]\+' "$jacc_file" | head -1)
    else
        jacc_val="MISSING"
    fi
 
    {
        echo "$pair"
        echo "  JSD:  $jsd_val"
        echo "  JACC: $jacc_val"
        echo
    } >> "$OUT"
done
 
echo "Wrote summary to $OUT"