import csv
import sys
import argparse
import os

csv.field_size_limit(sys.maxsize)

input_file = "CogNet-v2.0.tsv"

tags = {"es":"spa", "an":"arg", "fr":"fra", "oc":"oci"}

train_val_files_dict = {"es-an-train":"/CopperMT/ES-AN-RNN-0_RNN-213_S-0/inputs/split_data/es_an/inference/train_es_an.",
                        "es-an-val":"/CopperMT/ES-AN-RNN-0_RNN-213_S-0/inputs/split_data/es_an/inference/fine_tune_es_an.",
                        "fr-oc-train":"/CopperMT/FR-OC-RNN-0_RNN-251_S-0/inputs/split_data/fr_oc/inference/train_fr_oc.",
                        "fr-oc-val":"/CopperMT/FR-OC-RNN-0_RNN-251_S-0/inputs/split_data/fr_oc/inference/fine_tune_fr_oc.",
                        "fr-mfe-train":"/CopperMT/FR-MFE-RNN-0_RNN-102_S-0/inputs/split_data/fr_mfe/inference/train_fr_mfe.",
                        "fr-mfe-val":"/CopperMT/FR-MFE-RNN-0_RNN-102_S-0/inputs/split_data/fr_mfe/inference/fine_tune_fr_mfe.",
                        # "uz-kaa-train":"/CopperMT/UZ-KAA-RNN-0_RNN-264_S-0/inputs/split_data/uz_kaa/inference/train_uz_kaa.",
                        # "uz-kaa-val":"/CopperMT/UZ-KAA-RNN-0_RNN-264_S-0/inputs/split_data/uz_kaa/inference/fine_tune_uz_kaa."
                        }



def sanitize_and_dedupe(cognate_pairs, src, tgt, data_home):
    os.makedirs(f"Pipeline/true_cognate/data/", exist_ok=True)
    with open(f"Pipeline/true_cognate/data/true_cognates.{src}-{tgt}.{src}.txt", "w", encoding="utf-8") as f_src, \
        open(f"Pipeline/true_cognate/data/true_cognates.{src}-{tgt}.{tgt}.txt", "w", encoding="utf-8") as f_tgt:

        print(f"Total cognate pairs (may contain duplicates): {len(cognate_pairs)}")
        
        train_val_files = [f"{data_home}{train_val_files_dict[f'{src}-{tgt}-train']}",
                            f"{data_home}{train_val_files_dict[f'{src}-{tgt}-val']}"]

        train_val_cognate_pairs = load_train_data(train_val_files, src, tgt)
        print(f"Train and Val Pairs: {len(train_val_cognate_pairs)}")
        src_train = {src for src, tgt in train_val_cognate_pairs}
        tgt_train = {tgt for src, tgt in train_val_cognate_pairs}

        cleaned_cognate_pairs = [(src, tgt) for src, tgt in cognate_pairs if src not in src_train and tgt not in tgt_train]
        # cleaned_cognate_pairs = [(src, tgt) for src, tgt in cognate_pairs if (src, tgt) not in train_cognate_pairs]

        print(f"Sanitized pairs: {len(cleaned_cognate_pairs)}")

        cleaned_cognate_pairs = dedupe(cleaned_cognate_pairs)

        print(f"Deduped pairs: {len(cleaned_cognate_pairs)}")
        for (src_word, tgt_word) in cleaned_cognate_pairs:
            f_src.write("".join(src_word) + "\n")
            f_tgt.write("".join(tgt_word) + "\n")


    print(f"Done. Wrote {f_src} and {f_tgt}")


def process_tsv(src, tgt):
    with open(input_file, newline="", encoding="utf-8") as f_in:

        reader = csv.reader(f_in, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(reader)  # skip header

        cognate_pairs = []
        for row in reader:
            if not row:
                continue
            lang1, word1, lang2, word2 = row[1], row[2], row[3], row[4]

            if lang1 == tags[src] and lang2 == tags[tgt]:
                src_word, tgt_word = word1, word2
            elif lang1 == tags[tgt] and lang2 == tags[src]:
                src_word, tgt_word = word2, word1
            else:
                continue

            cognate_pairs.append((src_word, tgt_word))

        return cognate_pairs


def get_etymdb_cognates(src, tgt, etymdb_path):
    folder_path = os.path.join(etymdb_path, f"{src}_{tgt}")
    with open(f"{folder_path}/orig.{src}_{tgt}.{src}", "r") as src_file, \
         open(f"{folder_path}/orig.{src}_{tgt}.{tgt}", "r") as tgt_file:
        cognate_pairs = list(zip([s.strip() for s in src_file.readlines()], [t.strip() for t in tgt_file.readlines()]))
    print(f"EtymDB pairs: {len(cognate_pairs)}")
    return cognate_pairs

def dedupe(pairs):
    seen_src, seen_tgt = set(), set()
    deduped = []
    for src, tgt in pairs:
        if src in seen_src or tgt in seen_tgt:
            continue
        deduped.append((src, tgt))
        seen_src.add(src)
        seen_tgt.add(tgt)
    return deduped


def load_train_data(filenames, src, tgt):
    pairs = []
    for filename in filenames:
        with open(f"{filename}{tgt}", 'r') as tgt_datafile, \
             open(f"{filename}{src}", 'r') as src_datafile:
            tgt_spaced_words = tgt_datafile.readlines()
            src_spaced_words = src_datafile.readlines()
            assert len(tgt_spaced_words) == len(src_spaced_words)
            for src_spaced_word, tgt_spaced_word in zip(src_spaced_words, tgt_spaced_words):
                src_word = src_spaced_word.strip().replace(' ', '')
                tgt_word = tgt_spaced_word.strip().replace(' ', '')
                
                pairs.append((src_word, tgt_word))
    return pairs



def get_args():
    parser = argparse.ArgumentParser(description="Preprocess Cognate Files")
    parser.add_argument("--src", "-s")
    parser.add_argument("--tgt", "-t")
    parser.add_argument("--data_home", "-d")
    parser.add_argument("--etymdb_home", "-e")

    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()


    if f"{args.src}-{args.tgt}" in ["es-an", "fr-oc"]:
        cognate_pairs = process_tsv(args.src, args.tgt)
        cognate_pairs = cognate_pairs + get_etymdb_cognates(args.src, args.tgt, args.etymdb_home)
        sanitize_and_dedupe(cognate_pairs, args.src, args.tgt, args.data_home)

    if f"{args.src}-{args.tgt}" == "fr-mfe":
        cognate_pairs = get_etymdb_cognates(args.src, args.tgt, args.etymdb_home)
        sanitize_and_dedupe(cognate_pairs, args.src, args.tgt, args.data_home)


