#!/usr/bin/env python3
"""
Paired approximate randomization (AR) significance test for comparing two
systems' per-sentence scores (e.g. BLEURT scores_test files).

Usage:
    python paired_ar_significance.py scores_A.txt scores_B.txt \
        [--n-trials 10000] [--alpha 0.05] [--seed 0]

Each input file: one score per line, same sentence order, same length.

Null hypothesis: system A and system B are exchangeable (no real
difference). For each trial, each sentence's pair of scores is randomly
swapped (A<->B) with probability 0.5, simulating the null. The p-value is
the fraction of trials where the resulting |mean difference| is >= the
observed |mean difference|.
"""

import argparse
import numpy as np


def load_scores(path):
    with open(path) as f:
        scores = [float(line.strip()) for line in f if line.strip()]
    return np.array(scores)


def paired_ar_test(scores_a, scores_b, n_trials=10000, seed=0):
    assert len(scores_a) == len(scores_b), "Score files must have equal length (paired sentences)"

    rng = np.random.default_rng(seed)
    n = len(scores_a)

    diffs = scores_a - scores_b  # per-sentence paired differences
    observed_diff = diffs.mean()
    observed_abs = abs(observed_diff)

    # Random sign flips: with prob 0.5, swap A and B for a sentence,
    # which is equivalent to flipping the sign of that sentence's diff.
    signs = rng.choice([1.0, -1.0], size=(n_trials, n))
    trial_diffs = (signs * diffs).mean(axis=1)

    count_as_extreme = np.sum(np.abs(trial_diffs) >= observed_abs)
    # Add-one smoothing avoids a p-value of exactly 0.
    p_value = (count_as_extreme + 1) / (n_trials + 1)

    return {
        "mean_a": scores_a.mean(),
        "mean_b": scores_b.mean(),
        "observed_diff": observed_diff,
        "p_value": p_value,
    }


def main():
    parser = argparse.ArgumentParser(description="Paired approximate randomization test for two score files")
    parser.add_argument("scores_a", help="Path to system A's per-sentence scores file")
    parser.add_argument("scores_b", help="Path to system B's per-sentence scores file")
    parser.add_argument("--n-trials", type=int, default=10000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    scores_a = load_scores(args.scores_a)
    scores_b = load_scores(args.scores_b)

    result = paired_ar_test(
        scores_a, scores_b,
        n_trials=args.n_trials,
        seed=args.seed,
    )

    print(f"\nPaired Approximate Randomization with {args.n_trials} trials:")
    print(f"Results A ({args.scores_a}): mean = {result['mean_a']:.6f}")
    print(f"Results B ({args.scores_b}): mean = {result['mean_b']:.6f}")
    print(f"Observed difference (A - B): {result['observed_diff']:.6f}")
    print(f"p-value: {result['p_value']:.5f}\n\n")



if __name__ == "__main__":
    main()