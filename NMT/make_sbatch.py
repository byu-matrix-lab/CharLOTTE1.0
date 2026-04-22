import os
import shutil
import argparse
from tqdm import tqdm
import yaml

CONFIGS_DIR="NMT/configs/CONFIGS"
sbatch_template = """
#!/bin/bash

#SBATCH --time={walltime}   # walltime.  hours:minutes:seconds
#SBATCH --ntasks-per-node={n_tasks_per_node}
#SBATCH --nodes=1
#SBATCH --mem=1024000M
#SBATCH --gpus={n_gpus}
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user thebrendanhatch@gmail.com
#SBATCH --output ${DATA_HOME}/NMT/{LANG_OUT}/%j_%x.out
#SBATCH --job-name={name}
#SBATCH --qos={qos}
{partition}


python NMT/clean_slurm_outputs.py

nvidia-smi

# tensorboard --logdir "{tb_dir}" --port 6006 --host 0.0.0.0 &
srun {python_command}

python NMT/clean_slurm_outputs.py
""".strip()

def set_env(path=".env"):
    assert os.path.exists(path), f"NO .env FILE FOUND"
    with open(path) as env_file:
        for line in env_file:
            line = line.strip()
            if "#" in line:
                line = line.split("#")[0].strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())
set_env()
sbatch_template = os.path.expandvars(sbatch_template)

def main(configs_dir, mode, qos, out_dir, REVERSE_SRC_TGT):
    RTAG = ""
    if REVERSE_SRC_TGT:
        RTAG = ".REVERSE_SRC_TGT"

    out_dir = os.path.join(out_dir, mode + RTAG)
    if os.path.exists(out_dir):
        print("Deleting:", out_dir)
        shutil.rmtree(out_dir)
    print("Creating:", out_dir)
    os.makedirs(out_dir)

    for d in tqdm(os.listdir(configs_dir)):
        if d in ["data_log.csv", "data_params_log.csv", "_archive"]: continue
        if "data_params_log.csv" in d: continue
        d_config = os.path.join(configs_dir, d)
        d_out = os.path.join(out_dir, d + RTAG)
        assert not os.path.exists(d_out)
        os.mkdir(d_out)

        sbatch_fs = []
        for f in os.listdir(d_config):
            assert f.endswith(".yaml")
            f_config = os.path.join(d_config, f)
            config = read_config(f_config)
            f_out = os.path.join(d_out, f)[:-5] + RTAG + ".sh"
            assert not os.path.exists(f_out)
            
            python_command = f"python NMT/train.py \\\n\t--config \"{f_config}\" \\\n\t--mode {mode}"
            if REVERSE_SRC_TGT:
                python_command += f" \\\n\t--REVERSE_SRC_TGT"
            python_command += "\n"
            name=f"{mode}.{d}.{f[:-5]}"

            if mode == "TRAIN":
                n_gpus = config["n_gpus"]
            else:
                n_gpus = 1
            tb_dir = os.path.join(config["save"] + f"_TRIAL_s={config['seed']}", "tb")

            partition = ""
            if qos == "cs":
                partition = f"#SBATCH --partition={qos}"

            n_gpus_str = str(n_gpus)
            n_tasks_per_node = str(n_gpus)
            if qos == "cs":
                n_gpus_str = "a100:" + n_gpus_str

            if qos in ["cs"]:
                walltime = "24:00:00"
            else:
                walltime = "72:00:00"

            sbatch_content = sbatch_template.replace("{name}", name + RTAG) \
                .replace("{qos}", qos) \
                .replace("{python_command}", python_command) \
                .replace("{LANG_OUT}", d) \
                .replace("{n_gpus}", n_gpus_str) \
                .replace("{partition}", partition) \
                .replace("{n_tasks_per_node}", n_tasks_per_node) \
                .replace("{walltime}", walltime)

            
            lang_out_dir = "${DATA_HOME}/NMT/{d}"
            lang_out_dir = os.path.expandvars(lang_out_dir).replace("{d}", d)
            if not os.path.exists(lang_out_dir):
                os.makedirs(lang_out_dir)

            with open(f_out, "w") as outf:
                outf.write(sbatch_content + "\n")
            sbatch_fs.append(f_out)

        for training_type in ["PRETRAIN", "FINETUNE", "NMT", "AUGMENT"]:
            sh_path = os.path.join(d_out, f"all_{training_type}.sh")
            with open(sh_path, "w") as outf:
                for sf in sbatch_fs:
                    sf_name = sf.split("/")[-1]
                    if "CHAR" in sf_name or "TEST" in sf_name or "no_grad_clip" in sf_name:
                        continue
                    if sf_name.startswith(training_type):
                        outf.write(f"sbatch \"{sf}\"\n")
        

def read_config(f):
    with open(f) as inf:
        config = yaml.safe_load(inf)
    return config

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs_dir", default="NMT/configs/CONFIGS")
    parser.add_argument("--out", default="NMT/sbatch")
    parser.add_argument("--qos", default="matrix")
    parser.add_argument("--mode", choices=["TRAIN", "TEST", "INFERENCE", "ALL"], default="ALL")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    if args.mode in ["TRAIN", "ALL"]:
        main(
            configs_dir=args.configs_dir,
            mode="TRAIN",
            qos=args.qos,
            out_dir=args.out,
            REVERSE_SRC_TGT=False
        )
        main(
            configs_dir=args.configs_dir,
            mode="TRAIN",
            qos=args.qos,
            out_dir=args.out,
            REVERSE_SRC_TGT=True
        )

    if args.mode in ["TEST", "ALL"]:
        main(
            configs_dir=args.configs_dir,
            mode="TEST",
            qos=args.qos,
            out_dir=args.out,
            REVERSE_SRC_TGT=False
        )
        main(
            configs_dir=args.configs_dir,
            mode="TEST",
            qos=args.qos,
            out_dir=args.out,
            REVERSE_SRC_TGT=True
        )