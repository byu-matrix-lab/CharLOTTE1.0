import argparse
import os
import shutil
import json


SBATCH_TEMPLATE="""
#!/bin/bash

#SBATCH --time=24:00:00   # walltime.  hours:minutes:seconds
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=64000M
#SBATCH --gpus=a100:1
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user %u@byu.edu
#SBATCH --output Pipeline/slurm_outputs/hyper_param_search_outputs{tag}/%j_%x.out
#SBATCH --job-name=hyper_param_search.{NAME}
#SBATCH --qos cs
#SBATCH --partition cs

nvidia-smi

python Pipeline/clean_slurm_outputs.py
bash Pipeline/train_SC.sh {CFG}
python Pipeline/clean_slurm_outputs.py
rm core*
""".lstrip()

LEARNING_RATES = [0.001]
BATCH_SIZES = [16, 64, 256, 512]

EMBED_DIMS = [16, 32, 64, 128]
HIDDEN_DIMS = [16, 32, 64, 128, 256, 512]

LAYERS = [2, 4, 6]
ATTS = ["luong-dot"]

def make_stuff(
    out_dir
):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    params = []
    for lr in LEARNING_RATES:
        for batch_size in BATCH_SIZES:
            for e_dim in EMBED_DIMS:
                for h_dim in HIDDEN_DIMS:
                    for n_layers in LAYERS:
                        for att in ATTS:
                            params.append((lr, batch_size, e_dim, h_dim, n_layers, att))
    
    manifest = {}
    for idx, (lr, batch_size, e_dim, h_dim, n_layers, att) in enumerate(params):
        params_f = os.path.join(out_dir, f"{idx}.rnn.txt")
        assert idx not in manifest
        manifest[idx] = params_f
        content =   f"model_type=\"bigru\"\n"
        content +=  f"attention=\"{att}\"\n"
        content +=  f"enc_layer={n_layers}\n"
        content +=  f"enc_emb_dim={e_dim}\n"
        content +=  f"enc_hid_dim={h_dim}\n"

        content +=  f"dec_layer={n_layers}\n"
        content +=  f"dec_emb_dim={e_dim}\n"
        content +=  f"dec_hid_dim={h_dim}\n"

        content +=  f"batch_size={batch_size}\n"
        content +=  f"dropout=0.2\n"
        content +=  f"learning_rate={lr}\n"
        content +=  f"share_encoder=\"\"\n"
        content +=  f"share_decoder=\"\""
        with open(params_f, "w") as outf:
            outf.write(content)
    
    manifest_f = os.path.join(out_dir, "manifest.json")
    with open(manifest_f, "w") as outf:
        outf.write(json.dumps(manifest, ensure_ascii=False, indent=2))
    
    return manifest


def make_cfgs(
    cfgs,
    manifest,
    new_cfg_dir,
    sbatch_dir,
    tag
):
    keys = sorted([int(i) for i in manifest.keys()])
    ct_variations = 0
    sbatch_files = []
    for cfg_f in cfgs:
        print("Making variations of", cfg_f)
        for key in keys:
            sbatch_f = make_variation(
                cfg_f=cfg_f,
                idx=key,
                new_cfg_dir=new_cfg_dir,
                sbatch_dir=sbatch_dir,
                tag=tag
            )
            sbatch_files.append(sbatch_f)
            ct_variations += 1
    print(f"MADE {ct_variations} VARIATIONS")


def make_variation(cfg_f, idx, new_cfg_dir, sbatch_dir, tag):
    assert cfg_f.endswith(".cfg")
    with open(cfg_f) as inf:
        lines = [line.strip() for line in inf.readlines()]
    times = 0
    for l, line in enumerate(lines):
        if line.startswith("RNN_HYPERPARAMS_ID="):
            times += 1
            new_line = f"RNN_HYPERPARAMS_ID={idx}"
            lines[l] = new_line
    assert times == 1
    new_content = "\n".join(lines) + "\n"
    cfg_f_name = cfg_f.split("/")[-1]
    assert cfg_f_name.endswith(".cfg")
    new_cfg_f_name = cfg_f_name[:-3] + f"{idx}.cfg"
    new_cfg_f = os.path.join(new_cfg_dir, new_cfg_f_name)
    with open(new_cfg_f, "w") as outf:
        outf.write(new_content)
    
    sbatch_f = os.path.join(sbatch_dir, new_cfg_f_name + ".sh")
    if tag != "":
        tag = "_" + tag
    with open(sbatch_f, "w") as outf:
        sbatch_content = SBATCH_TEMPLATE.replace("{CFG}", new_cfg_f).replace("{NAME}", new_cfg_f_name).replace("{tag}", tag)
        outf.write(sbatch_content)
    return sbatch_f
    

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="Pipeline/rnn_hyperparams")
    parser.add_argument("--cfgs", required=True, help="comma-delimited list")
    parser.add_argument("--new_cfg_dir", default="Pipeline/cfg/SC-HYPERPARAM_SEARCH")
    parser.add_argument("--sbatch_dir", default="Pipeline/sbatch/hyper_param_search")
    parser.add_argument("--tag", default="")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    cfgs = [c.strip() for c in args.cfgs.split(",")]
    manifest = make_stuff(args.dir)
    if not os.path.exists(args.new_cfg_dir):
        os.mkdir(args.new_cfg_dir)
    make_cfgs(
        cfgs=cfgs,
        manifest=manifest,
        new_cfg_dir=args.new_cfg_dir,
        sbatch_dir=args.sbatch_dir,
        tag=args.tag
    )
