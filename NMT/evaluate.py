from sacrebleu.metrics import BLEU, CHRF

def calc_bleu(
    hyp, # list
    refs, # list of lists
    tokenize=None
):
    for ref in refs:
        if len(hyp) != len(ref):
            error = f"len hyp ({len(hyp)}) != len ref ({len(ref)})"
            error += "HYP:\n" + "\n".join(hyp[:3])
            error += "\nREF:\n" + "\n".join(ref[:3])
            raise ValueError(error)

    if tokenize is not None:
        bleu = BLEU(tokenize="char")
    else:
        bleu = BLEU()
    score = bleu.corpus_score(hyp, refs)
    print("BLEU STUFF")
    print(score)
    return score.score

def calc_chrF(
    hyp, # list
    refs # list of lists
):
    for ref in refs:
        if len(hyp) != len(ref):
            error = f"len hyp ({len(hyp)}) != len ref ({len(ref)})"
            error += "HYP:\n" + "\n".join(hyp[:3])
            error += "\nREF:\n" + "\n".join(ref[:3])
            raise ValueError(error)

    chrf = CHRF()
    score = chrf.corpus_score(hyp, refs)
    sentence_scores = []
    for i in range(len(hyp)):
        h = hyp[i]
        r = [refs[0][i]]
        sentence_scores.append(chrf.sentence_score(h, r).score)
    return score.score, sentence_scores

def read_data(f):
    with open(f) as inf:
        data = [line.strip() for line in inf.readlines()]
    return data

if __name__ == "__main__":
    print("###################")
    print("# NMT/evaluate.py #")
    print("###################")
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref")
    parser.add_argument("--hyp")
    parser.add_argument("--out")
    parser.add_argument("--REPLACE_UNK", action="store_true", default=False, help="if passed, will replace unknown tokens `?` and `>` with `<<unk>>` in reference")
    args = parser.parse_args()
    print("Arguments:")
    for k, v in vars(args).items():
        print(f"\t- {k}: `{v}`")
    
    ref = read_data(args.ref)
    if args.REPLACE_UNK:
        for rx, r in enumerate(ref):
            r = r.replace("?", "<<unk>>")
            r = r.replace(">", "<<unk>>")
            ref[rx] = r

    hyp = read_data(args.hyp)

    bleu_score = calc_bleu(hyp=hyp, refs=[ref])
    chrf_score, chrf_sent_scores = calc_chrF(hyp=hyp, refs=[ref])

    print("BLUE:", bleu_score)
    print("chrF:", chrf_score)

    with open(args.out, "w") as outf:
        outf.write("Scores:\n")
        outf.write(f"\tREF: {args.ref}\n")
        outf.write(f"\tHYP: {args.hyp}\n")
        outf.write(f"\nBLEU: {bleu_score}\nchrF: {chrf_score}\n")

