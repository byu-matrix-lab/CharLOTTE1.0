import argparse
import os
import xlsxwriter # have to import this into cop_mt so that we can use fairseq to check model size
from xlsxwriter.color import Color
from tqdm import tqdm
import datetime
import sys
import torch
from fairseq import checkpoint_utils, utils

WITH_ATT = {"EN-DJK"}

def get_lang_pair_tag(src_lang, tgt_lang):
    lang_pair_tag = f"{src_lang.upper()}-{tgt_lang.upper()}"
    if lang_pair_tag in WITH_ATT:
        lang_pair_tag += ".ATT"
    return lang_pair_tag

def compile(
    langs,
    rnn_hyperparams_dir,
    COPPERMT,
    seed,
    out_dir,
    tag,
    sbatch_dir,
    smt_sbatch_dir
):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    now = datetime.datetime.now()
    timestamp = now.strftime('%m_%d_%Y_%H:%M')
    tag_dir = os.path.join(out_dir, f"{tag}_{timestamp}")
    if not os.path.exists(tag_dir):
        os.mkdir(tag_dir)

    BEST_LANG_CONFIGS = {}

    header = {
        "RNN_ID": 0,
        "model_type": 1,
        "attention": 2, 
        "enc_layer": 3,
        "enc_emb_dim": 4, 
        "enc_hid_dim": 5,
        "dec_layer": 6,
        "dec_emb_dim": 7,
        "dec_hid_dim": 8,
        "batch_size": 9,
        "dropout": 10,
        "learning_rate": 11,
        "model_size":12,
        "BLEU": 13
    }

    REDOS = {}

    for lang in langs:
        print("LANG:", lang)
        src_lang, tgt_lang = tuple(lang.split("-"))
        lang_pair_tag = get_lang_pair_tag(src_lang, tgt_lang)
        lang_pair_tuple = (src_lang, tgt_lang)
        out_f = os.path.join(tag_dir, f"{lang}.results.xlsx")
        if os.path.exists(out_f):
            print("Removing:", out_f)
            os.remove(out_f)
        
        lang_workbook = xlsxwriter.Workbook(out_f)
        header_format = lang_workbook.add_format({"bold": True})
        rnn_id_format = lang_workbook.add_format({"bold": True, "bg_color": Color("#DFDFE1"), "align": "right"})
        BLEU_format = lang_workbook.add_format({"bg_color": Color("#AFC7F7")})
        best_BLEU_format = lang_workbook.add_format({"bold": True, "bg_color": Color("#78A3FA")})
        param_format = lang_workbook.add_format({"align": "right"})
        
        assert lang not in BEST_LANG_CONFIGS
        BEST_LANG_CONFIGS[lang] = {
            "BLEU": {}
        }

        worksheet = lang_workbook.add_worksheet()
        for key, idx in header.items():
            worksheet.write(0, idx, key, header_format)

        visited_rnn_ids = set()
        BEST_BLEU = None
        for f in tqdm(os.listdir(rnn_hyperparams_dir) + ["SMT"]):
            if f == "SMT":
                results_rnn_params = {
                    "model_type": "SMT",
                    "attention": "n/a",
                    "enc_layer": "n/a",
                    "enc_emb_dim": "n/a",
                    "enc_hid_dim": "n/a",
                    "dec_layer": "n/a",
                    "dec_emb_dim": "n/a",
                    "dec_hid_dim": "n/a",
                    "batch_size": "n/a",
                    "dropout": "n/a",
                    "learning_rate": "n/a",
                    "share_encoder": "n/a",
                    "share_decoder": "n/a"
                }
                rnn_id = get_smt_id(rnn_hyperparams_dir=rnn_hyperparams_dir)
                assert rnn_id not in visited_rnn_ids
                assert int(rnn_id) not in visited_rnn_ids
                COPPERMT_results_dir = os.path.join(COPPERMT, f"{lang_pair_tag}-SMT-{seed}_SMT-null_S-{seed}")
                scores_f = os.path.join(COPPERMT_results_dir, f"inputs/split_data/{src_lang}_{tgt_lang}/{seed}/fine_tune_{src_lang}_{tgt_lang}.{tgt_lang}.hyp.scores.txt.wo_replace_unk.txt")
            else:
                f_path = os.path.join(rnn_hyperparams_dir, f)
                if os.path.isdir(f_path): continue
                if f == "manifest.json": continue

                print("checking that", f, "ends with .rnn.txt")
                assert f.endswith(".rnn.txt")
                split_f = f.split(".")
                assert len(split_f) == 3
                rnn_id = split_f[0]
                assert isinstance(rnn_id, str)
                assert rnn_id not in visited_rnn_ids
                assert int(rnn_id) not in visited_rnn_ids

                rnn_params = read_rnn_params_f(f_path)

                COPPERMT_results_dir = os.path.join(COPPERMT, f"{lang_pair_tag}-RNN-{seed}_RNN-{rnn_id}_S-{seed}")
                results_rnn_params_f = os.path.join(COPPERMT_results_dir, f"inputs/parameters/bilingual_default/default_parameters_rnn_{lang}.txt")
                results_rnn_params = read_rnn_params_f(results_rnn_params_f)

                print("asserting rnn_params == results_rnn_params")
                assert rnn_params == results_rnn_params
                print("\tpassed :)")
                scores_f = os.path.join(COPPERMT_results_dir, f"workspace/reference_models/bilingual/rnn_{src_lang}-{tgt_lang}/0/results/test_on_val_selected_checkpoint_{src_lang}_{tgt_lang}.{tgt_lang}/generate-valid.hyp.scores.txt.wo_replace_unk.txt")
                model_f = os.path.join(COPPERMT_results_dir, f"workspace/reference_models/bilingual/rnn_{src_lang}-{tgt_lang}/0/checkpoints/checkpoint_best.pt")

            
            if os.path.exists(scores_f):
                print("READING BLEU FROM", scores_f)
                BLEU = read_scores(scores_f)
            else:
                BLEU = -1
                if lang_pair_tuple not in REDOS:
                    REDOS[lang_pair_tuple] = []
                REDOS[lang_pair_tuple].append((rnn_id, f))
                print("Scores file does not exist:", scores_f)

            if os.path.exists(model_f):
                print('READING MODEL SIZE FROM', model_f)
                model_size = get_model_size(model_f)
            else:
                model_size = 0
                print("Model size could not be read:", model_f)

            assert rnn_id not in visited_rnn_ids
            assert int(rnn_id) not in visited_rnn_ids
            visited_rnn_ids.add(rnn_id)

            worksheet.write(int(rnn_id) + 1, header["RNN_ID"], rnn_id, rnn_id_format)
            for param, param_val in results_rnn_params.items():
                if param in ["share_encoder", "share_decoder"]: continue
                worksheet.write(int(rnn_id) + 1, header[param], param_val, param_format)
            worksheet.write(int(rnn_id) + 1, header["BLEU"], BLEU, BLEU_format)
            worksheet.write(int(rnn_id) + 1, header["model_size"], model_size)

            if BEST_BLEU is None:
                BEST_BLEU = (int(rnn_id) + 1, header["BLEU"], BLEU, BLEU_format)
                BEST_LANG_CONFIGS[lang]["BLEU"]["params"] = results_rnn_params
                BEST_LANG_CONFIGS[lang]["BLEU"]["BLEU"] = BLEU
                BEST_LANG_CONFIGS[lang]["BLEU"]["rnn_id"] = rnn_id
            else:
                if BLEU > BEST_BLEU[2]:
                    BEST_BLEU = (int(rnn_id) + 1, header["BLEU"], BLEU, BLEU_format)
                    BEST_LANG_CONFIGS[lang]["BLEU"]["params"] = results_rnn_params
                    BEST_LANG_CONFIGS[lang]["BLEU"]["BLEU"] = BLEU
                    BEST_LANG_CONFIGS[lang]["BLEU"]["rnn_id"] = rnn_id

        worksheet.write(BEST_BLEU[0], BEST_BLEU[1], BEST_BLEU[2], best_BLEU_format)

        worksheet.autofit()
        lang_workbook.close()

    best_out_f = os.path.join(tag_dir, "best_configs.xlsx")
    best_workbook = xlsxwriter.Workbook(best_out_f)
    best_header_format = best_workbook.add_format({"bold": True})
    best_rnn_id_format = best_workbook.add_format({"bold": True, "bg_color": Color("#DFDFE1"), "align": "right"})
    best_best_BLEU_format = best_workbook.add_format({"bold": True, "bg_color": Color("#78A3FA")})
    best_param_format = lang_workbook.add_format({"align": "right"})
    
    best_worksheet = best_workbook.add_worksheet()
    best_worksheet.write(0, 0, "LANG", best_header_format)
    best_worksheet.write(0, 1, "CRITERIA", best_header_format)
    for key, idx in header.items():
        best_worksheet.write(0, idx + 2, key, best_header_format)
    best_worksheet.write(0, len(header) + 2, "TRAIN / VAL / TEST SIZE", best_header_format)
    for lx, (lang, criteria_configs) in enumerate(BEST_LANG_CONFIGS.items()):
        source_lang, target_lang = tuple(lang.split("-"))
        for cx, (criteria, configs) in enumerate(criteria_configs.items()):
            if configs["params"]['model_type'] == "bigru":
                model_id = configs['rnn_id']
                MODEL_TYPE = "RNN"
            else:
                print("NOT RNN:", configs["params"]['model_type'])
                assert configs["params"]['model_type'] == "SMT"
                model_id = "null"
                MODEL_TYPE = "SMT"
            lang_pair_tag = get_lang_pair_tag(source_lang, target_lang)
            split_data_dir = os.path.join(COPPERMT, f"{lang_pair_tag}-{MODEL_TYPE}-{seed}_{MODEL_TYPE}-{model_id}_S-{seed}/inputs/split_data/{source_lang}_{target_lang}/{seed}")
            train_size, val_size, test_size = get_train_val_test_sizes(split_data_dir, src=source_lang, tgt=target_lang)
            best_worksheet.write((lx * 2) + cx + 1, 0, lang, best_header_format)
            best_worksheet.write((lx * 2) + cx + 1, 1, criteria, best_header_format)
            best_worksheet.write((lx * 2) + cx + 1, len(header) + 2, f"{train_size:,} / {val_size:,} / {test_size:,}", best_header_format)
            for key, idx in header.items():
                if key in configs["params"]:
                    best_worksheet.write((lx * 2) + cx + 1, idx + 2, configs["params"][key], best_param_format)
                elif key == "RNN_ID":
                    best_worksheet.write((lx * 2) + cx + 1, idx + 2, configs["rnn_id"], best_rnn_id_format)
                elif key == "BLEU":
                    best_worksheet.write((lx * 2) + cx + 1, idx + 2, configs["BLEU"], best_best_BLEU_format)
    best_worksheet.autofit()
    best_workbook.close()

    redos_out = os.path.join(tag_dir, "REDOS.sbatch.sh")
    with open(redos_out, "w") as outf:
        for (src_lang, tgt_lang), rnn_ids in REDOS.items():
            att_tag = ""
            if get_lang_pair_tag(src_lang, tgt_lang).endswith(".ATT"):
                att_tag = ".ATT"
            for rnn_id, f in rnn_ids:
                if f != "SMT":
                    file_path = os.path.join(sbatch_dir, f"{src_lang}-{tgt_lang}{att_tag}.{rnn_id}.cfg.sh")
                else:
                    file_path = os.path.join(smt_sbatch_dir, f"{src_lang}-{tgt_lang}{att_tag}.smt.cfg.sh")
                outf.write(f"sbatch {file_path}\n")
    
def get_train_val_test_sizes(split_data_dir, src, tgt):
    train_f = os.path.join(split_data_dir, f"train_{src}_{tgt}.{src}")
    val_f = os.path.join(split_data_dir, f"fine_tune_{src}_{tgt}.{src}")
    test_f = os.path.join(split_data_dir, f"test_{src}_{tgt}.{src}")
    train_lines = read_lines(train_f)
    val_lines = read_lines(val_f)
    test_lines = read_lines(val_f)
    return len(train_lines), len(val_lines), len(test_lines)


def read_lines(f):
    with open(f) as inf:
        lines = [l.strip() for l in inf.readlines()]
    return lines

def get_smt_id(rnn_hyperparams_dir):
    max_rnn_id = None
    for f in os.listdir(rnn_hyperparams_dir):
        f_path = os.path.join(rnn_hyperparams_dir, f)
        if os.path.isdir(f_path): continue
        if f == "manifest.json": continue

        split_f = f.split(".")
        assert len(split_f) == 3
        rnn_id = int(split_f[0])
        if max_rnn_id is None:
            max_rnn_id = rnn_id
        else:
            if rnn_id > max_rnn_id:
                max_rnn_id = rnn_id

    smt_rnn_id = max_rnn_id + 1
    return smt_rnn_id

def read_scores(f):
    with open(f) as inf:
        lines = [l.rstrip() for l in inf.readlines()]
    BLEU = None
    for l, line in enumerate(lines):
        if l == 0:
            assert line == "Scores:"
        elif l == 1:
            assert line.startswith("\tREF: ")
        elif l == 2:
            assert line.startswith("\tHYP: ")
        elif l == 3:
            assert line == ""
        elif l == 4:
            assert line.startswith("BLEU_DETAILS: BLEU = ")
        elif l == 5:
            assert line.startswith("BLEU_SCORE: ")
            BLEU = float(line.strip().split("BLEU_SCORE: ")[-1])
            break
    assert BLEU is not None
    return BLEU

def get_model_size(f):
    # 1. Add CopperMT directories to Python's search path
    # (Using both root and child dirs ensures any internal relative imports don't break)
    sys.path.append("/home/pbickel/CharLOTTE1.0/CopperMT/CopperMT") # need to add CharLOTTE home
    sys.path.append("/home/pbickel/CharLOTTE1.0/CopperMT/CopperMT/pipeline/neural_translation")

    # 2. Force Python to execute the file containing the registration decorator
    import pipeline.neural_translation.multilingual_rnns.multilingual_rnn
    # Point directly to the neural_translation root directory
    user_dir = "/home/pbickel/CharLOTTE1.0/CopperMT/CopperMT/pipeline/neural_translation"
    
    # This forces fairseq to load CopperMT's custom registry
    utils.import_user_module(argparse.Namespace(user_dir=user_dir))

    # Now fairseq can successfully look up 'multilingual_bigru'
    ensemble, cfg, task = checkpoint_utils.load_model_ensemble_and_task([f])
    model = ensemble[0]

    total_params = sum(p.numel() for p in model.parameters())
    return total_params

def read_rnn_params_f(f):
    print("READING PARAMS f", f)
    params = {}
    with open(f) as inf:
        lines = [l.strip() for l in inf.readlines()]
    for line in lines:
        f, v = tuple(line.split("="))
        if v.endswith("\""):
            assert v.startswith("\"")
        if v.startswith("\""):
            assert v.endswith("\"")
            v = v[1:-1]
        assert f not in params
        params[f] = v
    return params

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs", help="comma-delimited list")
    parser.add_argument("--rnn_hyperparams_dir", default="Pipeline/rnn_hyperparams")
    parser.add_argument("--COPPERMT")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="Pipeline/hyperparam_search_results")
    parser.add_argument("--tag")
    parser.add_argument("--sbatch_dir", default="Pipeline/sbatch/hyperparam_search", help="folder of sbatch scripts for hyperparam search. This is for making the redos script.")
    parser.add_argument("--smt_sbatch_dir", default="Pipeline/sbatch/smt", help="folder of smt sbatch scripts for hyperparam search. This is for making the redos script.")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    langs = [l.strip() for l in args.langs.split(",")]
    compile(
        langs=langs,
        rnn_hyperparams_dir=args.rnn_hyperparams_dir,
        COPPERMT=args.COPPERMT,
        seed=args.seed,
        out_dir=args.out,
        tag=args.tag,
        sbatch_dir=args.sbatch_dir,
        smt_sbatch_dir=args.smt_sbatch_dir
    )
