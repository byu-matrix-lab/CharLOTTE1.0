#!/bin/bash

set -euo pipefail

DIR="NMT/delta_metrics/results"
OUT="$DIR/metric_oc_diff_results_summary.txt"

> "$OUT"

for f in "$DIR"/metric_oc_diff.*.txt; do
    [ -e "$f" ] || continue

    base=$(basename "$f")
    pair=${base#metric_oc_diff.}
    pair=${pair%.txt}

    {
        echo "$pair"
        # print each non-empty line, trimmed, indented
        sed 's/^[[:space:]]*//; s/[[:space:]]*$//' "$f" | sed '/^$/d' | sed 's/^/  /'
        echo
    } >> "$OUT"
done

echo "Wrote summary to $OUT"