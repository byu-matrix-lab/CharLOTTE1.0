import argparse
import Levenshtein
import statistics
import numpy as np

def read_lines(f):
    with open(f) as inf:
        data = [l.rstrip() for l in inf.readlines()]
    return data

def get_diffs(sents1, sents2):
    if len(sents1) != len(sents2):
        raise ValueError(f"len sents1 ({len(sents1)}) is different than len sents2 ({len(sents2)})")
    
    diff_len_sents = []
    nleds = []
    for i in range(len(sents1)):
        s1 = sents1[i]
        s2 = sents2[i]
        words1 = s1.split()
        words2 = s2.split()
        if len(words1) != len(words2):
            diff_len_sents.append(i)
        nled_value = nled(s1, s2)
        nleds.append(nled_value)
    assert len(nleds) == len(sents1) == len(sents2)
    avg_nled = sum(nleds) / len(nleds)
    med_nled = statistics.median(nleds)
    hist, edges = np.histogram(nleds, bins=50)
    hist = hist.tolist()
    edges = edges.tolist()
    hist_per = [num / len(sents1) for num in hist]

    metrics = {
        "total": len(sents1),
        "avg_nled": avg_nled,
        "med_nled": med_nled,
        "hist": hist,
        "hist_per": hist_per,
        "edges": edges,
        "total_diff_len_sents": len(diff_len_sents),
        "diff_len_sents": diff_len_sents
    }
    return metrics

def get_word_diff(sents1, sents2):
    words1 = get_words(sents1)
    words2 = get_words(sents2)
    if len(words1) != len(words2):
        raise ValueError(f"words1 ({len(words1)}) has different length than words2 ({len(words2)})")
    
    diff = 0
    diff_word_nleds = []
    i = 0
    for w1 in words1:
        w2 = words2[i]
        if w1 != w2:
            nled_value = nled(w1, w2)
            diff_word_nleds.append(nled_value)
            diff += 1
        i += 1
    
    avg_diff_word_nled = sum(diff_word_nleds) / len(diff_word_nleds)
    med_diff_word_nled = statistics.median(diff_word_nleds)
    hist, edges = np.histogram(diff_word_nleds, bins=10)
    hist = hist.tolist()
    edges = edges.tolist()
    hist_per = [num / len(diff_word_nleds) for num in hist]

    metrics = {
        "total": len(words1),
        "num_different": diff,
        "ratio_different": diff / len(words1),
        "percent_different": round(diff / len(words1) * 100, 2),
        "avg_nled_of_diff_words": avg_diff_word_nled,
        "med_nled_of_diff_words": med_diff_word_nled,
        "hist_nled_of_diff_words": hist,
        "edges_nled_of_diff_words": edges,
        "hist_per_nled_of_diff_words": hist_per
    }
    return metrics


def get_words(sents):
    words = []
    for sent in sents:
        words += sent.split()
    return words

def nled(seq1, seq2):
    max_len = max(len(seq1), len(seq2))
    distance = Levenshtein.distance(seq1, seq2)
    normalized = distance / max_len
    return normalized


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pl_sents", required=True)
    parser.add_argument("--pl_prime_sents", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    pl_sents = read_lines(args.pl_sents)
    pl_prime_sents = read_lines(args.pl_prime_sents)

    print("getting diffs")
    scores = get_diffs(pl_sents, pl_prime_sents)
    print("getting word_diffs")
    scores["word_scores"] = get_word_diff(pl_sents, pl_prime_sents)

    with open(args.out, 'w') as outf:
        outf.write(f'S-NLD: {scores["avg_nled"]}\n')
        outf.write(f'  %WA: {scores["word_scores"]["percent_different"]}\n')
        outf.write(f'W-NLD: {scores["word_scores"]["avg_nled_of_diff_words"]}')