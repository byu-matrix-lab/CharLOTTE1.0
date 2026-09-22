from tqdm import tqdm
import argparse
import Levenshtein
from collections import defaultdict
import math
import csv
from functools import lru_cache
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks
import ast
import random
import os
import xlsxwriter
import subprocess

def main(results_f="es-an-213.output.txt", counts_f='counts/es-an_counts.txt', lang_pair="es-an", ngram_size=5, frequency=10):
    """Filter the most meaningful ngram mappings from the OC model.
    Parameters:
        results_f (str): The filepath of the results file from the OC model
        counts_f (str): The filepath of the file with counts of how many times each word appears in PL NMT training data (created when transforming data)
        lang_pair (str): language pair being analyzed
        ngram size (int): size of largest ngrams
        frequency (int): Filter out all ngrams that appear less than this number
    """
    results = read_CopperMT_Results(results_f)
    counts, applied_counts = get_counts_no_gaps(results, ngram_size, counts_f)

    kept = []
    rows = sorted((len(i), entropy(counts[i]), -sum(counts[i].values()), i, dict(counts[i])) for i in counts) # sorted by length, entropy, frequency
    d_top = [] # most frequent mapping for each ngram
    for _, ent, freq, ngram, alignments in tqdm(rows, desc="filtering low frequency and identity"):
        top = max(alignments, key=alignments.get)
        d_top.append((ngram, top))
        if sum(alignments.values()) < frequency: # 1. filter out the low frequency mappings
            continue
        if top == ngram: # 2. filter out mappings that are mostly the identity -> must be itself at least 50 percent of the time
            if (alignments[top] / -freq) < .5:
                pass
            else:
                continue
        kept.append((ngram, top))

    raw_f = f"raw/{lang_pair}.ng_{ngram_size}.fr_{frequency}.csv"

    with open(raw_f, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["entropy", "ngram", "alignments"])
        for ngram, top in sorted(kept, key=lambda x: (entropy(counts[x]), -sum(counts[x].values()))): # sorted by entropy, frequency
            alignments = dict(counts[ngram])
            ent = entropy(counts[ngram])
            writer.writerow([round(ent, 2), ngram, dict(sorted(alignments.items(), key=lambda x: -x[1]))])

    # 3. calculate entropy based on distribution
    entropy_threshold = entropy_dist_kde(raw_f, lang_pair, ngram_size=ngram_size, zeros=False)
    
    final_kept = [] # final filtered list of input ngrams
    for ngram, top in tqdm(kept, desc='filtering redundant rules'):
        if should_keep(counts, d_top, ngram, top, entropy_threshold, frequency): # 4. only filters based on entropy threshold for explainers and input ngram frequency, NOT non-identity mappings
            final_kept.append(ngram)


    with open(f"filtered/{lang_pair}.ng_{ngram_size}.fr_{frequency}.ent_{round(entropy_threshold, 2)}.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["entropy", "ngram", "alignments"])
        for ngram in sorted(final_kept, key=lambda x: (entropy(counts[x]), -sum(counts[x].values()))): # sorted by entropy, frequency
            alignments = dict(counts[ngram])
            ent = entropy(counts[ngram])
            if ent <= entropy_threshold:
                writer.writerow([round(ent, 2), ngram, dict(sorted(alignments.items(), key=lambda x: -x[1]))])

    with open(f"filtered_applied_counts/{lang_pair}.ng_{ngram_size}.fr_{frequency}.ent_{round(entropy_threshold, 2)}.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["entropy", "ngram", "alignments"])
        for ngram in sorted(final_kept, key=lambda x: (entropy(counts[x]), -sum(counts[x].values()))): # sorted by entropy, frequency
            alignments = dict(applied_counts[ngram])
            ent = entropy(counts[ngram])
            if ent <= entropy_threshold:
                writer.writerow([round(ent, 2), ngram, dict(sorted(alignments.items(), key=lambda x: -x[1]))])  

    return

def all_ngrams(results_f="es-an-213.output.txt", lang_pair="es-an", ngram_size=5, counts_f="counts/es-an_counts.txt"):
    """Print all mappings to a file, accounting for insertions and deletions."""
    results = read_CopperMT_Results(results_f)

    counts, applied_counts = get_counts_no_gaps(results, ngram_size, counts_f)

    # all ngrams by entropy with gaps removed
    with open(f"{lang_pair}_ngrams.ng_{ngram_size}.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["entropy", "ngram", "alignments"])
        rows = sorted((len(i), entropy(counts[i]), -sum(counts[i].values()), i, dict(counts[i])) for i in counts) # size of ngram, entropy, total input frequency
        for _, ent, _, ngram, alignments in rows:
            writer.writerow([round(ent, 2), ngram, dict(sorted(alignments.items(), key=lambda x: -x[1]))])

def print_mappings(results_f="es-an-213.output.txt", lang_pair="es-an"):
    """Write the PL, PL' pairs from the OC model to a file"""
    results = read_CopperMT_Results(results_f)
    with open(f"mappings/{lang_pair}.txt", "w") as f:
        total_char = 0
        for key in results:
            total_char += len(key)
            f.write(f"{key} --> {results[key]}\n")
    
    print(f"{lang_pair} PL word mappings character count: {total_char}")


    
def entropy_dist_kde(raw_f, lang_pair="es-an", ngram_size=5, frequency=10, zeros=False):
    """Calculate and return the entropy threshold using Gaussian KDE with prominence"""
    counts = read_counts_csv(raw_f)
    
    entropies = []
    for i, c in counts.items():
        if sum(c.values()) < frequency:
            continue
        if i == max(c, key=c.get):
            continue
        e = entropy(c)
        if zeros or e != 0:
            entropies.append(e)

    X = np.array(entropies)
    np.save(f'entropies/{lang_pair}.npy', X)
    
    kde = gaussian_kde(X, bw_method='silverman')
    kde.set_bandwidth(kde.factor * .5)

    # Evaluate density on a grid
    x_grid = np.linspace(X.min(), X.max(), 1000)
    density = kde(x_grid)

    # Find local minima (valleys) with prominence
    valley_idx, props = find_peaks(-density, prominence=.05 * density.max())

    threshold = x_grid[valley_idx[0]]
    print(f"Threshold: {round(threshold, 2)}")


    fig, ax = plt.subplots(figsize=(8,5))
    ax.hist(X, bins=100, density=True)
    ax.plot(x_grid, density, lw=2, label='KDE')
    ax.scatter(x_grid[valley_idx], density[valley_idx], color='red', zorder=5, label='Prominent Minima')
    # fig.suptitle(f"{lang_pair} KDE")
    plt.plot(threshold, density[valley_idx[0]], 'ro', markersize=8, label=f'Threshold: {threshold:.2f}')
    plt.axvline(x=threshold, color='r', linestyle='--', alpha=0.5)
    ax.set_xlabel('Entropy (bits)')
    ax.set_ylabel('Density')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'entropy_distributions/{lang_pair}.KDE.prominent_valley.png')
    plt.clf()
    
    return threshold

def get_stats(data_home):
    """Compile the results for all of the entropy files."""
    results = {}
    seed = 0 # for samples
    all_lang_pairs = []
    # filtered rules, frequency within word types
    for filename in os.listdir('filtered'):
        lang_pair = filename.split('.')[0]
        all_lang_pairs.append(lang_pair)
        counts = read_counts_csv(f'filtered/{filename}')
        rows = sorted((entropy(counts[i]), -sum(counts[i].values()), i, dict(counts[i])) for i in counts) # sorted by length, entropy, frequency

        all_mappings = len(rows)
        random.seed(seed)
        seed += 1
        samples = random.sample(range(1, all_mappings - 1), 28)
        samples.append(0)
        samples.append(all_mappings - 1)
        results[lang_pair] = {}
        
        entropy0 = 0
        entropy0_num = 0
        
        all_mappings_num = 0
        noisy_mappings_num = 0
        with open(f"samples/{lang_pair}.txt", 'w') as outfile:
            for i, (ent, _, ngram, alignments) in enumerate(rows):
                if i in samples:
                    freq_str = ', '.join(f'{k}:{v}' for k, v in alignments.items())
                    latex = f"{i + 1} & \\texttt{{{escape(ngram)}}} & \\texttt{{{escape(freq_str)}}} & {ent:.2f} \\\\\n"
                    outfile.write(latex)
                top = max(alignments, key=alignments.get)
                if ent == 0:
                    entropy0 += 1
                    entropy0_num += alignments[top]
                all_mappings_num += alignments[top]
                for key in alignments.keys():
                    if key == ngram or key == top:
                        continue
                    noisy_mappings_num += alignments[key]
            results[lang_pair]['0_rules'] = entropy0
            results[lang_pair]['0_rules_frequency'] = entropy0_num
            results[lang_pair]['all_rules'] = all_mappings
            results[lang_pair]['all_rules_frequency'] = all_mappings_num
            results[lang_pair]['noisy_mappings'] = noisy_mappings_num

        # filtered rules, frequency within NMT training data
        counts_ = read_counts_csv(f'filtered_applied_counts/{filename}')
        rows = sorted((entropy(counts[i]), -sum(counts_[i].values()), i, dict(counts_[i])) for i in counts_) # sorted by length, entropy, frequency

        all_mappings = len(rows)
        results[f"{lang_pair}_applied"] = {}
        
        entropy0 = 0
        entropy0_num = 0
        all_mappings_num = 0
        noisy_mappings_num = 0
        for i, (ent, _, ngram, alignments) in enumerate(rows):
            top = max(alignments, key=alignments.get)
            if ent == 0:
                entropy0 += 1
                entropy0_num += alignments[top]
            all_mappings_num += alignments[top]
            for key in alignments.keys():
                if key == ngram or key == top:
                    continue
                noisy_mappings_num += alignments[key]
        results[f"{lang_pair}_applied"]['0_rules'] = entropy0
        results[f"{lang_pair}_applied"]['0_rules_frequency'] = entropy0_num
        results[f"{lang_pair}_applied"]['all_rules'] = all_mappings
        results[f"{lang_pair}_applied"]['all_rules_frequency'] = all_mappings_num
        results[f"{lang_pair}_applied"]['noisy_mappings'] = noisy_mappings_num

    # make xlsx file
    headers = [
    'Language Pair',
    'Type (0-entropy)',
    'Type (all)',
    'Word (0-entropy-count)',
    'Word (0-entropy-density)',
    'Word (all-count)',
    'Word (all-density)',
    'Applied (0-entropy-count)',
    'Applied (0-entropy-density)',
    'Applied (all-count)',
    'Applied (all-density)']
 
    workbook = xlsxwriter.Workbook('results.xlsx')
    ws = workbook.add_worksheet('Sheet1')
    
    bold = workbook.add_format({'font_name': 'Arial', 'bold': True})
    normal = workbook.add_format({'font_name': 'Arial'})
    density = workbook.add_format({'font_name': 'Arial', 'num_format': '0.000'})

    density_cols = {4, 6, 8, 10}
    
    for col, h in enumerate(headers):
        ws.write(0, col, h, bold)
    
    for row_idx, lp in enumerate(all_lang_pairs, start=1):
        base = results[lp]
        applied = results[f'{lp}_applied']
        word_char_count = get_character_counts(lp)
        applied_char_count = get_applied_character_counts(data_home, lp)
    
        row = [
            lp,
            base['0_rules'],
            base['all_rules'],
            base['0_rules_frequency'],
            base['0_rules_frequency'] / word_char_count,
            base['all_rules_frequency'],
            base['all_rules_frequency'] / word_char_count,
            applied['0_rules_frequency'],
            applied['0_rules_frequency'] / applied_char_count,
            applied['all_rules_frequency'],
            applied['all_rules_frequency'] / applied_char_count,
        ]
        for col, val in enumerate(row):
            fmt = density if col in density_cols else normal
            ws.write(row_idx, col, val, fmt)
    
    for col, h in enumerate(headers):
        max_len = len(h)
        for lp in all_lang_pairs:
            max_len = max(max_len, len(str(lp)) if col == 0 else 12)
        ws.set_column(col, col, max_len + 3)
    
    workbook.close()

    return

def get_character_counts(lang_pair):
    mappings_f = f"mappings/{lang_pair}.txt"
    total_chars = 0
    with open(mappings_f, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            try:
                pl, _, pl_prime = line.strip().split(' ')
            except:
                pl, _, _, pl_prime = line.strip().split(' ')
            total_chars += len(pl)
    return total_chars

def get_applied_character_counts(data_home, lang_pair):
    pl, cl = lang_pair.split('-')
    file = f"{data_home}/data/CharLOTTE_data/{pl}-en/train.{pl}.txt"
    cmd = f"tr -d '\\n' < {file} | wc -m"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return int(result.stdout.strip())

### Helper Functions ###
def escape(s):
    return s.replace('_', '\\_').replace('$', '\\$').replace('^', '\\^{}')

def read_counts_csv(filepath):
    counts = defaultdict(lambda: defaultdict(int))
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ngram = row["ngram"]
            alignments = ast.literal_eval(row["alignments"])
            for target, count in alignments.items():
                counts[ngram][target] = count
    return counts


def get_counts_no_gaps(results, ngram_size, counts_f):
    """Gets counts for all the ngrams after deleting gap characters from the alignment. 
    Deals with insertions and deletions properly.
    For example, if _g_ -> che: 1,
                    _g -> ch : 40,
                    g -> h : 45, 
                 then the combined tally would be:
                    g -> che: 1:, ch: 39, h: 5
    """
    nmt_counts = {}
    with open(counts_f, 'r') as nmt_counts_file:
        lines = nmt_counts_file.readlines()
        for line in lines:
            word, c = line.split(',')[0], line.split(',')[-1]
            nmt_counts[word] = int(c.strip())

    applied_counts = defaultdict(lambda: defaultdict(int))

    print(f"total NMT training data word replacements: {sum(nmt_counts.values())}")
    d = defaultdict(lambda: defaultdict(int))

    for n in range(1, ngram_size + 1):
        for key in tqdm(results, desc=f"getting {n}-grams"):
            a1, a2 = get_alignments(f"${key}$", f"${results[key]}$") # adding $ as word boundaries
            for c1, c2 in zip(ngrams(a1, n), ngrams(a2, n)):
                # check insertion
                idx = a1.find(c1)
                left = idx - 1
                right = idx + n 
                if left in range(len(a1)):
                    if a1[left] == "_":
                        continue
                if right in range(len(a1)):
                    if a1[right] == "_":
                        continue
                # check deletion
                idx = a2.find(c2)
                left = idx - 1
                right = idx + n 
                if left in range(len(a2)):
                    if a2[left] == "_":
                        continue
                if right in range(len(a2)):
                    if a2[right] == "_":
                        continue
                d[c1.replace("_", "")][c2.replace("_", "")] += 1

                try:
                    applied_counts[c1.replace("_", "")][c2.replace("_", "")] += nmt_counts[key]
                except KeyError:
                    # print(key)
                    pass
    return d, applied_counts

def get_counts(results):
    """Gets counts for every ngram, but includes the gap characters in the ngrams"""
    d = defaultdict(lambda: defaultdict(int))

    for n in range(1, 6):
        for key in results:
            a1, a2 = get_alignments(f"${key}$", f"${results[key]}$") # adding $ as word boundaries
            for c1, c2 in zip(ngrams(a1, n), ngrams(a2, n)):
                
                d[c1][c2] += 1
    return d

def get_alignments(src, tgt, gap='_'):
    """Align two words with Levenshtein character alignment"""
    ops = Levenshtein.editops(src, tgt)
    a1, a2 = list(src), list(tgt)
    offset1 = offset2 = 0

    for op, i, j in ops:
        if op == 'insert':        # gap in s1
            a1.insert(i + offset1, gap)
            offset1 += 1
        elif op == 'delete':      # gap in s2
            a2.insert(j + offset2, gap)
            offset2 += 1
        # 'replace': no gap needed, characters already paired

    return ''.join(a1), ''.join(a2)

def entropy(counts):
    """Calculate entropy for a dictionary"""
    total = sum(counts.values())
    n = len(counts)
    if n <= 1:
        return 0.0
    return -sum((c/total) * math.log2(c/total) for c in counts.values())
    
def ngrams(s, n):
    """Split a word into all possible ngrams"""
    return [s[i:i+n] for i in range(len(s) - n + 1)]

def is_explained_by(ngram, target, explainers):
    """Check if ngram -> target is fully explained by any combination of explainer mappings."""
    @lru_cache(maxsize=None)
    def dp(i, j):
        if i == len(ngram) and j == len(target): # reached end of both strings, base case
            return True
        for short_ng, short_tgt in explainers: # each possible starting point for the transformation
            ni, nj = i + len(short_ng), j + len(short_tgt) # new indices if transformation is applied
            if ngram[i:i+len(short_ng)] == short_ng and target[j:j+len(short_tgt)] == short_tgt: # see if that transformation didn't actually change the source string
                if dp(ni, nj): # check the rest of the string
                    return True
        return False
    
    result = dp(0, 0)
    dp.cache_clear()
    return result

def should_keep(d, d_top, ngram, top, entropy_threshold, frequency):
    ent = entropy(d[ngram])
    l = len(ngram)
    if ent <= entropy_threshold:
        # explainers = [(ng, tgt) for ng, tgt in d_top if (entropy(d[ng]) <= entropy_threshold and len(ng) < l and sum(d[ng].values()) >= frequency)] # any smaller ngram with entropy below threshold and high enough frequency
        explainers = [(ng, tgt) for ng, tgt in d_top if ((len(ng) < l) and (ng in ngram) and (tgt in top) and (sum(d[ng].values()) >= frequency) and (entropy(d[ng]) <= entropy_threshold))]
        if is_explained_by(ngram, top, explainers):
            return False
    return True

def read_CopperMT_Results(results_f, RETURN_SPACED=False, log_p_thresh=None):
    with open(results_f) as inf:
        lines = [line.strip() for line in inf.readlines()]

    data_rows = []
    for lx, line in enumerate(lines):
        split_line = line.split("|")
        if "4 | = | 9" in line or '1 6 | 2 0 |' in line:
            split_line = line
            print("exception made for | occuring in word")
        if len(split_line) == 4:
            assert split_line[1].strip() == "INFO"
            continue
        elif line.startswith("Generate test with beam="):
            continue
        elif line.startswith("Generate valid with beam="):
            continue
        else:
            # should be a good line :)
            assert any([
                line.startswith("S-"),
                line.startswith("T-"),
                line.startswith("H-"),
                line.startswith("D-"),
                line.startswith("P-"),
            ]), f"line ({lx}) `{line}` does not begin with S-, T-, H-, D-, or P-"
            data_rows.append(line)

    print("Blocking CopperMT")
    data = []
    block = []
    for i, line in tqdm(enumerate(data_rows), total=len(data_rows)):
        if i > 0 and i % 5 == 0:
            data.append(tuple(block))
            block = []
        block.append(line.strip())
    if len(block) > 0:
        assert len(block) == 5
        data.append(tuple(block))

    print("Getting Copper MT results")
    results = {}
    visited_ids = set()
    ct_low_conf = 0
    for S, T, H, D, P in tqdm(data):
        assert S.startswith("S-")
        assert T.startswith("T-")
        assert H.startswith("H-")
        assert D.startswith("D-")
        assert P.startswith("P-")

        s_id = int(S.split()[0].strip().split("-")[1])
        S = S.split("\t")[-1].strip()
        t_id = int(T.split()[0].strip().split("-")[1])
        T = T.split("\t")[-1].strip()
        h_conf = float(H.split("\t")[-2].strip())
        h_id = int(H.split()[0].strip().split("-")[1])
        H = H.split("\t")[-1].strip()
        d_id = int(D.split()[0].strip().split("-")[1])
        D = D.split("\t")[-1].strip()

        assert s_id == t_id == h_id == d_id
        assert h_id not in visited_ids
        visited_ids.add(h_id)

        assert H == D

        if RETURN_SPACED:
            source = S
            hyp = H
        else:
            source = "".join(S.split())
            hyp = "".join(H.split())
        if log_p_thresh and h_conf <= log_p_thresh:
            print("RNN confidence <= threshold, setting hyp=source")
            hyp = source
            ct_low_conf += 1
        if source in results:
            print("SOURCE IN RESULTS")
            print("source:", source)
            print("hyp:", hyp)
            print(f"results['{source}']:", results[source])
        if "<unk>" not in source:
            assert source not in results
            results[source] = hyp
        else:
            if source not in results:
                results[source] = hyp
            else:
                if isinstance(results[source], str):
                    results[source] = [results[source]]
                assert isinstance(results[source], list)
                if hyp not in results[source]:
                    results[source].append(hyp)

    print(f"RNN: NUMBER OF LOW CONFIDENCE (< {log_p_thresh}) PREDICTIONS: {ct_low_conf} / {len(data)} unique words predicted, {round((ct_low_conf / len(data)) * 100, 2)}%")
    return results


def bandwidth_ablation(lang_pair):
    "Must be run after main"
    X = np.load(f"entropies/{lang_pair}.npy")
    X = np.asarray(X).flatten()
    resolution = 10

    print(lang_pair)
    result = []
    valid_thresh = []
    for bandwidth in np.linspace(.2, .8, resolution):
        for prominence_val in np.linspace(.01, .1, resolution):
            kde = gaussian_kde(X, bw_method='silverman')
            kde.set_bandwidth(kde.factor * bandwidth)

            # Evaluate density on a grid
            x_grid = np.linspace(X.min(), X.max(), 1000)
            density = kde(x_grid)

            # Find local minima (valleys) with prominence
            valley_idx, props = find_peaks(-density, prominence=prominence_val * density.max())

            try:
                threshold = x_grid[valley_idx[0]]
                result.append((bandwidth, prominence_val, threshold))
                valid_thresh.append(threshold)
            except: # no prominent minima
                result.append((bandwidth, prominence_val, 0))

    result = np.array(result)
    bandwidths = np.unique(result[:, 0])
    prominences = np.unique(result[:, 1])

    grid = result[:, 2].reshape(len(bandwidths), len(prominences))
    mask = grid == 0  # no valid minimum found

    fig, ax = plt.subplots(figsize=(7, 6))
    masked_grid = np.ma.masked_array(grid, mask=mask)

    im = ax.imshow(masked_grid, origin='lower', aspect='auto', cmap='viridis',
                extent=[prominences.min(), prominences.max(),
                        bandwidths.min(), bandwidths.max()])

    ax.imshow(np.ma.masked_array(np.ones_like(grid), mask=~mask),
            origin='lower', aspect='auto', cmap='gray_r', alpha=0.3,
            extent=[prominences.min(), prominences.max(),
                    bandwidths.min(), bandwidths.max()])

    ax.set_xlabel('Prominence (fraction of max density)')
    ax.set_ylabel('Bandwidth scale')
    ax.set_title('Threshold value across bandwidth × prominence')
    fig.colorbar(im, ax=ax, label='Entropy threshold')
    plt.tight_layout()
    os.makedirs("bandwidth_ablation", exist_ok=True)
    plt.savefig(f'bandwidth_ablation/{lang_pair}_sensitivity_heatmap.png', dpi=150)
    plt.clf()

    valid_thresh = np.array(valid_thresh)
    print(f"Average: {np.sum(valid_thresh) / len(valid_thresh)}")
    min = np.min(valid_thresh)
    max = np.max(valid_thresh)
    print(f"Min: {min}, Max: {max}")
    print(f"Range: {max - min}")
    return

def get_args():
    parser = argparse.ArgumentParser(description="Filter Meaningful Mappings")

    parser.add_argument('--oc_output_path', '-p', type=str, default="es-an-213.output.txt", help="Path to OC output")
    parser.add_argument('--counts_path', '-c', type=str, default='counts/es-an_counts.txt', help='file containing counts for all words in SMT training data')
    parser.add_argument('--language_pair', '-l', type=str, default="es-an", help="Language Pair")
    parser.add_argument('--ngram_size', '-n', type=int, default=5, help="Check ngrams of size up until this number")
    parser.add_argument('--frequency', '-f', type=int, default=10, help="Filter out all ngrams that appear less than this number")
    parser.add_argument('--all_ngrams', '-a', action='store_true', help="Print out list of all ngrams with their mappings and entropy to a separate file")
    parser.add_argument('--compile_results', '-r', action='store_true', help='only compile the results, nothing else')
    parser.add_argument('--mappings', '-m', action='store_true', help="Print out list of all word mappings to a separate file")
    parser.add_argument('--bandwidth_ablation', '-b', action='store_true', help="Bandwidth ablation for given language pair. Must be run after main")
    parser.add_argument('--data_home', '-d', type=str, help="path to data_home, only needed for compiling results")

    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    
    if args.compile_results:
        get_stats(args.data_home)

    elif args.bandwidth_ablation:
        bandwidth_ablation(args.language_pair)

    else:
        if args.mappings:
            print_mappings(args.oc_output_path, args.language_pair)

        if args.all_ngrams:
            all_ngrams(args.oc_output_path, args.language_pair, args.ngram_size)
        
        main(args.oc_output_path, args.counts_path, args.language_pair, args.ngram_size, args.frequency)
