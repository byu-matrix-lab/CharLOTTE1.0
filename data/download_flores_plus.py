import huggingface_hub
from datasets import load_dataset
import os
import shutil
from datetime import datetime
from tqdm import tqdm
import argparse
from argparse import ArgumentParser, Namespace


def log_parsed_args(f):
    def wrapper():
        args = f()
        if not isinstance(args, Namespace):
            raise ValueError(f"To use log_parsed_args decorator, function must return object type argparse.Namespace.")
        print("Arguments:")
        for arg, value in vars(args).items():
            print(f"\t-{arg}=`{value}` ({type(value)})")
        print("\n\n")
        return args
    return wrapper

def main(out_dir, auth_token, langs:list):
    if os.path.exists(out_dir):
        print("DELETING", out_dir)
        shutil.rmtree(out_dir)
    print("CREATING", out_dir)
    os.mkdir(out_dir)
    notes_path = os.path.join(out_dir, "notes.txt")

    huggingface_hub.login(token=auth_token)

    starttime = datetime.now()
    start = starttime.strftime("%m-%d-%Y %H:%M:%S")
    ds_full = load_dataset("openlanguagedata/flores_plus")

    print("\nDEV")
    dev = ds_full["dev"]
    dev, dev_langs = get_data(dev, get_langs=langs)
    print("\nWRITING DEV")
    write_data(dev, dev_langs, out_dir, subdir="dev")

    print("\nDEVTEST")
    devtest = ds_full["devtest"]
    devtest, devtest_langs = get_data(devtest, get_langs=langs)
    print("\nWRITING DEVTEST")
    write_data(devtest, devtest_langs, out_dir, subdir="devtest")

    endtime = datetime.now()
    end = endtime.strftime("%m-%d-%Y %H:%M:%S")
    with open(notes_path, "w") as outf:
        outf.write("SOURCE: https://huggingface.co/datasets/openlanguagedata/flores_plus,\n\tand for Aragonese, https://huggingface.co/datasets/openlanguagedata/flores_plus/blob/main/dataset_cards/arg_Latn.md\n")
        outf.write(f"Download began {start}\n")
        outf.write(f"Download ended {end}\n")

def get_data(dataset, get_langs:list=None):
    visited = set()
    data = {}
    langs = set()
    for item in tqdm(dataset):
        lang = item["iso_639_3"]
        script = item["iso_15924"]
        glotto = item["glottocode"]
        l = f"{lang}_{script}_{glotto}"

        if get_langs and l not in get_langs:
            continue

        idx = item["id"]
        if idx not in data:
            data[idx] = {}

        assert l not in data[idx]
        text = item["text"]
        data[idx][l] = text
        langs.add(l)

        assert (idx, lang, script, glotto) not in visited
        visited.add((idx, lang, script, glotto))
    
    for idx in data:
        assert set(data[idx].keys()) == langs
    return data, langs

def write_data(dataset, langs, out_dir, subdir="dev"):
    outsubdir = os.path.join(out_dir, subdir)
    assert not os.path.exists(outsubdir)
    os.mkdir(outsubdir)

    lang_data = {l: [] for l in langs}

    idxs = sorted([int(ix) for ix in dataset.keys()])

    assert list(range(len(dataset))) == idxs

    for idx in range(len(dataset)):
        assert set(dataset[idx].keys()) == langs
        for lang in langs:
            lang_data[lang].append(dataset[idx][lang])
    
    for lang, data in lang_data.items():
        f = os.path.join(outsubdir, f"{lang}.{subdir}")
        with open(f, "w") as outf:
            for line in data:
                outf.write(line.strip() + "\n")

@log_parsed_args
def get_args():
    parser = ArgumentParser()
    parser.add_argument("-o", "--out_dir")
    parser.add_argument("-t", "--auth_token")
    parser.add_argument("-l", "--langs", help="comma-delimited list")
    args = parser.parse_args()
    if args.langs:
        args.langs = [l.strip() for l in args.langs.split(",")]
    return args

if __name__ == "__main__":
    print("###########################")
    print("# download_flores_plus.py #")
    print("###########################")
    args = get_args()
    main(**vars(args))
