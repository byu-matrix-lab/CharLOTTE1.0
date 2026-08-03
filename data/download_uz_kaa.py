import argparse
import os
from tqdm import tqdm
from datasets import load_dataset
import huggingface_hub


def oldi(uz_kaa_output, kaa_en_output):
    # load dataset
    dilmash_corpus = load_dataset("tahrirchi/dilmash")

    def write_col(dataset_split, col, path):
        with open(path, "w") as f:
            f.write("\n".join(dataset_split[col]) + "\n")

    write_col(dilmash_corpus["kaa_uzb"], "src_sent", f"{uz_kaa_output}/kaa.txt")
    write_col(dilmash_corpus["kaa_uzb"], "tgt_sent", f"{uz_kaa_output}/uz.txt")

    write_col(dilmash_corpus["kaa_eng"], "src_sent", f"{kaa_en_output}/kaa.txt")
    write_col(dilmash_corpus["kaa_eng"], "tgt_sent", f"{kaa_en_output}/en.txt")

    return

def flores_plus(auth_token, uz_dev_output, uz_devtest_output, kaa_devtest_output):
    huggingface_hub.login(token=auth_token)
    
    dataset = load_dataset("openlanguagedata/flores_plus", "uzn_Latn")

    with open(uz_devtest_output, "w") as f:
        f.write("\n".join(dataset["devtest"]["text"]) + "\n")

    with open(uz_dev_output, "w") as f:
        f.write("\n".join(dataset["dev"]["text"]) + "\n")

    dataset = load_dataset("openlanguagedata/flores_plus", "kaa_Latn")

    with open(kaa_devtest_output, "w") as f:
        f.write("\n".join(dataset["devtest"]["text"]) + "\n")

    return

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--auth_token", type=str)
    parser.add_argument("--uz_kaa_output", type=str)
    parser.add_argument("--kaa_en_output", type=str)
    parser.add_argument("--uz_dev_output", type=str)
    parser.add_argument("--uz_devtest_output", type=str)
    parser.add_argument("--kaa_devtest_output", type=str)

    return parser.parse_args()

if __name__ == "__main__":
    print("-----------------------------------")
    print("###### download_uz_kaa.py ######")
    print("-----------------------------------")
    args = get_args()

    flores_plus(args.auth_token, args.uz_dev_output, args.uz_devtest_output, args.kaa_devtest_output)

    oldi(args.uz_kaa_output, args.kaa_en_output)

   