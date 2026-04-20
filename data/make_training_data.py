import argparse
from NMT.assert_no_data_overlap import assert_no_overlap
import copy
import json
import os
import shutil

def main(
    src_train:list,
    tgt_train:list,

    src_val:str,
    tgt_val:str,

    src_test:str,
    tgt_test:str,

    src_lang:str,
    tgt_lang:str,

    out_dir:str
):
    assert src_train is not None
    assert tgt_train is not None
    assert src_lang is not None
    assert tgt_lang is not None
    assert out_dir is not None

    if src_val is None:
        assert tgt_val is None
    if tgt_val is None:
        assert src_val is None
    
    if src_test is None:
        assert tgt_test is None
    if tgt_test is None:
        assert src_test is None
    
    # OUT DIR
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    pair_dir = os.path.join(out_dir, f"{src_lang}-{tgt_lang}")
    if os.path.exists(pair_dir):
        print("DELETING", pair_dir)
        shutil.rmtree(pair_dir)
    print("CREATING", pair_dir)
    os.mkdir(pair_dir)

    # DEDUPE THE TRAINING DATA
    train = []
    for src_train_f, tgt_train_f in zip(src_train, tgt_train):
        train += get_pairs(src_train_f, tgt_train_f)
    print("\n\nDEDUPING THE TRAINING DATA")
    train = dedupe_data(train)

    val = get_pairs(src_val, tgt_val)
    test = get_pairs(src_test, tgt_test)

    print("TRAIN:", len(train))
    print("VAL:", len(val))
    print("TEST:", len(test))

    # ENSURE NO OVERLAP BETWEEN TRAIN / DEV / TEST
    print("\n\nREMOVING OVERLAP WITH VAL/TEST")
    new_train, new_val = remove_overlap(train, val, test)
    assert new_val == val # this shouldn't change for our data

    passed, results = assert_no_overlap(
        train=new_train,
        dev=new_val,
        test=test,
        VERBOSE=False
    )
    print(json.dumps(results, indent=2))

    assert passed == True
    print("LEN NEW TRAIN:", len(new_train))
    print("LEN NEW VAL:", len(new_val))
    print("LEN TEST:", len(test))

    # WRITE TO FILE
    write_set(pair_dir, new_train, src_lang, tgt_lang, div="train")
    write_set(pair_dir, new_val, src_lang, tgt_lang, div="val")
    write_set(pair_dir, test, src_lang, tgt_lang, div="test")

def dedupe_data(data):
    print("BEFORE:", len(data))
    used = set()
    deduped = []
    for item in data:
        if item not in used:
            deduped.append(item)
            used.add(item)
    print("AFTER:", len(deduped))
    return deduped

def get_pairs(src_file, tgt_file):
    if src_file == None or tgt_file == None:
        return []

    print(f"READING PARALLEL DATA:\n\t-`{src_file}`\n\t-`{tgt_file}`")
    src_lines = read_file(src_file)
    tgt_lines = read_file(tgt_file)
    assert len(src_lines) == len(tgt_lines)
    return list(zip(src_lines, tgt_lines))

def read_file(f):
    with open(f) as inf:
        lines = [l.strip() for l in inf.readlines()]
    return lines

def write_set(pair_dir, pairs, src_lang, tgt_lang, div="train"):
    print(f"Writing {src_lang}-{tgt_lang} {div} to {pair_dir}")
    assert div in ["train", "test", "val"]
    src_path = os.path.join(pair_dir, f"{div}.{src_lang}.txt")
    tgt_path = os.path.join(pair_dir, f"{div}.{tgt_lang}.txt")
    write_pairs(src_path, tgt_path, pairs)

def write_pairs(src_f, tgt_f, pairs):
    with open(src_f, "w") as sf, open(tgt_f, "w") as tf:
        for src_line, tgt_line in pairs:
            sf.write(src_line.strip() + "\n")
            tf.write(tgt_line.strip() + "\n")

def remove_overlap(train_set, fine_tune_set, test_set):
    train_pairs = copy.deepcopy(train_set)
    fine_tune_pairs = copy.deepcopy(fine_tune_set)
    test_pairs = copy.deepcopy(test_set)

    fine_tune_src_set, fine_tune_tgt_set =      get_src_tgt_sets(fine_tune_pairs)
    test_src_set, test_tgt_set =                get_src_tgt_sets(test_pairs)

    new_train_pairs = []
    for train_src_seg, train_tgt_seg in train_pairs:
        REMOVE = False
        if any([
            train_src_seg in fine_tune_src_set,
            train_src_seg in test_src_set,

            train_tgt_seg in fine_tune_tgt_set,
            train_tgt_seg in test_tgt_set
        ]):
            REMOVE = True
        if not REMOVE:
            new_train_pairs.append((train_src_seg, train_tgt_seg))
    
    new_fine_tune_pairs = []
    for fine_tune_src_seg, fine_tune_tgt_seg in fine_tune_pairs:
        REMOVE = False
        if any([
            fine_tune_src_seg in test_src_set,

            fine_tune_tgt_seg in test_tgt_set
        ]):
            REMOVE = True
        if not REMOVE:
            new_fine_tune_pairs.append((fine_tune_src_seg, fine_tune_tgt_seg))
            
    return new_train_pairs, new_fine_tune_pairs

def get_src_tgt_sets(pairs):
    src_set = set([src for src, tgt in pairs])
    tgt_set = set([tgt for src, tgt in pairs])
    return src_set, tgt_set

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src_train", required=True, help="comma-delimited list of files. Must correspond with --tgt_train.")
    parser.add_argument("--tgt_train", required=True, help="comma-delimited list of files. Must correspond with --src_train.")

    parser.add_argument("--src_val", default=None)
    parser.add_argument("--tgt_val", default=None)

    parser.add_argument("--src_test", default=None)
    parser.add_argument("--tgt_test", default=None)

    parser.add_argument("--src_lang", required=True)
    parser.add_argument("--tgt_lang", required=True)

    parser.add_argument("--out_dir", required=True)

    args = parser.parse_args()

    args.src_train = [f.strip() for f in args.src_train.split(",")]
    args.tgt_train = [f.strip() for f in args.tgt_train.split(",")]
    assert len(args.src_train) == len(args.tgt_train)

    return args

if __name__ == "__main__":
    args = get_args()
    main(
        src_train=args.src_train,
        tgt_train=args.tgt_train,

        src_val=args.src_val,
        tgt_val=args.tgt_val,

        src_test=args.src_test,
        tgt_test=args.tgt_test,

        src_lang=args.src_lang,
        tgt_lang=args.tgt_lang,

        out_dir=args.out_dir
    )
