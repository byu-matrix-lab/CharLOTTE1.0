# CharLOTTE1.0_public — Cleanup Plan

Plan for sanitizing the repo for public release: removing hardcoded personal paths, personal email, and incomplete/broken references throughout.

---

## 1. Environment variable setup (foundational)

Everything else depends on this step.

- Rename `HOME` → `CHARLOTTE_HOME` in `.env`. Bash has a built-in `$HOME` (the user's home directory); sourcing a `.env` that sets `HOME=...` would overwrite it, breaking `cd ~` and other tools.
- Keep `DATA_HOME` as-is (no conflict).
- Add `.env` to `.gitignore`.
- Create `.env.example` documenting what both variables should be set to, so users know what to fill in.

`.env.example`:
```bash
CHARLOTTE_HOME=/path/to/CharLOTTE1.0_public
DATA_HOME=/path/to/external/data/and/models
```

---

## 2. Shell infrastructure — `train_SC.sh` and `pred_SC.sh`

Both scripts `source $1` (the `.cfg` file) without first loading `.env`. Add `source .env` before `source $1` so that `${CHARLOTTE_HOME}` and `${DATA_HOME}` are defined when the `.cfg` is evaluated.

Also fix the **hardcoded BYU HPC conda path** (`/vapps/rhel9/x86_64/miniconda3/latest/bin/conda`) in both files. Replace with a portable snippet that finds conda dynamically via `conda info --base`. Same fix applies to `setup.sh`.

Files:
- `Pipeline/train_SC.sh`
- `Pipeline/pred_SC.sh`
- `setup.sh`

---

## 3. `.cfg` files — replace hardcoded paths (6 files)

Since these are sourced by bash after `.env` is loaded (step 2), all hardcoded paths can be replaced with `${CHARLOTTE_HOME}` and `${DATA_HOME}`. Example diff for `es-an.cfg`:

```bash
# before
MODULE_HOME_DIR=/home/hatch5o6/Cognate/code
PARALLEL_TRAIN=/home/hatch5o6/Cognate/code/NMT/data/CharLOTTE/PLAIN/es-an/train.csv
COGNATE_TRAIN=/home/hatch5o6/nobackup/archive/data/COGNATE_TRAIN/es-an
COPPERMT_DATA_DIR=/home/hatch5o6/nobackup/archive/CopperMT
COPPERMT_DIR=/home/hatch5o6/Cognate/code/CopperMT/CopperMT
PARAMETERS_DIR=/home/hatch5o6/Cognate/code/Pipeline/parameters
RNN_HYPERPARAMS=/home/hatch5o6/Cognate/code/Pipeline/rnn_hyperparams

# after
MODULE_HOME_DIR=${CHARLOTTE_HOME}
PARALLEL_TRAIN=${CHARLOTTE_HOME}/NMT/data/CharLOTTE/PLAIN/es-an/train.csv
COGNATE_TRAIN=${DATA_HOME}/data/COGNATE_TRAIN/es-an
COPPERMT_DATA_DIR=${DATA_HOME}/CopperMT
COPPERMT_DIR=${CHARLOTTE_HOME}/CopperMT/CopperMT
PARAMETERS_DIR=${CHARLOTTE_HOME}/Pipeline/parameters
RNN_HYPERPARAMS=${CHARLOTTE_HOME}/Pipeline/rnn_hyperparams
```

The commented-out `CogNet` paths at the bottom of each `.cfg` also need updating.

Files:
- `Pipeline/cfg/SC/es-an.cfg`
- `Pipeline/cfg/SC/fr-mfe.cfg`
- `Pipeline/cfg/SC/fr-oc.cfg`
- `Pipeline/cfg/SC_SMT/es-an.smt.cfg`
- `Pipeline/cfg/SC_SMT/fr-mfe.smt.cfg`
- `Pipeline/cfg/SC_SMT/fr-oc.smt.cfg`

---

## 4. YAML configs — two-part fix (15 files + 1 code change)

### 4a. Modify `NMT/train.py:read_config()`

YAML has no native variable substitution. Python's `os.path.expandvars()` expands `$VAR` / `${VAR}` from environment variables. Modify `read_config()` to:
1. Load `.env` into `os.environ` (using `python-dotenv` or a simple manual loader).
2. Call `os.path.expandvars()` on every string value in the config dict after parsing.

This is a ~10 line change.

### 4b. Update all 15 YAML files

Three to four keys need updating in each config. Example:

```yaml
# before
save: /home/hatch5o6/nobackup/archive/CognateMT/PredictCognates/an-en/PRETRAIN.es-en
from_pretrained: /home/hatch5o6/nobackup/archive/CognateMT/PredictCognates/an-en/PRETRAIN.es-en_TRIAL_s=1000
train_data: /home/hatch5o6/Cognate/code/NMT/data/CharLOTTE/PLAIN/es-en/train.csv
spm: /home/hatch5o6/nobackup/archive/CognateMT/spm_models/es-an_en/es-an_en/es-an_en

# after
save: ${DATA_HOME}/CognateMT/PredictCognates/an-en/PRETRAIN.es-en
from_pretrained: ${DATA_HOME}/CognateMT/PredictCognates/an-en/PRETRAIN.es-en_TRIAL_s=1000
train_data: ${CHARLOTTE_HOME}/NMT/data/CharLOTTE/PLAIN/es-en/train.csv
spm: ${DATA_HOME}/CognateMT/spm_models/es-an_en/es-an_en/es-an_en
```

Files:
- `NMT/configs/CONFIGS/an-en/NMT.an-en.yaml`
- `NMT/configs/CONFIGS/an-en/PRETRAIN.es-en.yaml`
- `NMT/configs/CONFIGS/an-en/PRETRAIN.SC_es2an-en.yaml`
- `NMT/configs/CONFIGS/an-en/FINETUNE.es-en>>an-en.yaml`
- `NMT/configs/CONFIGS/an-en/FINETUNE.SC_es2an-en>>an-en.yaml`
- `NMT/configs/CONFIGS/mfe-en/NMT.mfe-en.yaml`
- `NMT/configs/CONFIGS/mfe-en/PRETRAIN.fr-en.yaml`
- `NMT/configs/CONFIGS/mfe-en/PRETRAIN.SC_fr2mfe-en.yaml`
- `NMT/configs/CONFIGS/mfe-en/FINETUNE.fr-en>>mfe-en.yaml`
- `NMT/configs/CONFIGS/mfe-en/FINETUNE.SC_fr2mfe-en>>mfe-en.yaml`
- `NMT/configs/CONFIGS/oc-en/NMT.oc-en.yaml`
- `NMT/configs/CONFIGS/oc-en/PRETRAIN.fr-en.yaml`
- `NMT/configs/CONFIGS/oc-en/PRETRAIN.SC_fr2oc-en.yaml`
- `NMT/configs/CONFIGS/oc-en/FINETUNE.fr-en>>oc-en.yaml`
- `NMT/configs/CONFIGS/oc-en/FINETUNE.SC_fr2oc-en>>oc-en.yaml`

---

## 5. Python files — individual fixes (8 files)

### `Pipeline/make_SC_training_data.py`
- Replace `sys.path.append("/home/hatch5o6/Cognate/code/NMT")` with a path derived from `__file__`:
  ```python
  sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "NMT"))
  ```
- Remove the `# TODO Fix this` comment.

### `Pipeline/write_scripts.py`
- Remove unused `COPPERMT_DIR` constant (line 4).
- In the `parameters_stensil` template, replace hardcoded `MOSES_DIR` with `${CHARLOTTE_HOME}/CopperMT/CopperMT/submodules`.
- In the `sbatch_preamble` template, replace hardcoded slurm output path with a `${CHARLOTTE_HOME}`-relative path and remove the personal email line (`--mail-user`).

### `Pipeline/make_hyperparam_search_space.py`
- In the sbatch template string: replace the hardcoded `--output` path and the `rm /home/hatch5o6/Cognate/code/core*` line with `${CHARLOTTE_HOME}`-relative equivalents.
- Change all argparse `default=` values from hardcoded paths to `None`.

### `Pipeline/compile_hyperparam_search_results.py`
- Change all 5 argparse `default=` values (lines 336–342) from hardcoded paths to `None`.

### `NMT/hr_CopperMT.py`
- Replace the two hardcoded result `.json` file paths (lines 203, 216) with paths derived from `__file__` or a new CLI argument.

### `NMT/evaluate.py`
- Replace the hardcoded COMET model path (line 50) with `os.environ.get("COMET_MODEL_PATH")`, raising a clear error if it is unset.

### `NMT/build_loss_graph.py`
- Change the argparse `default=` (line 86) from a hardcoded path to `None` (make the argument required).

### `NMT/assert_no_data_overlap.py`
- Change the argparse `default=` (line 411) from a hardcoded path to `None` (make the argument required).

---

## 6. sbatch and shell utility scripts (9 files)

### `Pipeline/sbatch/` (6 files)
These are example job submission scripts. For each:
- Remove the `--mail-user thebrendanhatch@gmail.com` line (or replace with a placeholder comment like `#SBATCH --mail-user your@email.com`).
- Replace the hardcoded `#SBATCH --output` path with a relative path (e.g., `Pipeline/slurm_outputs/...`). Note: `#SBATCH` directives are expanded from the submission environment, so `${CHARLOTTE_HOME}` will work if the user has it set when calling `sbatch`.
- In the script body, add `source .env` and replace hardcoded paths with `${CHARLOTTE_HOME}`-relative ones.

Files:
- `Pipeline/sbatch/predict/es-an.213.cfg.sh`
- `Pipeline/sbatch/predict/fr-mfe.102.cfg.sh`
- `Pipeline/sbatch/predict/fr-oc.251.sh`
- `Pipeline/sbatch/smt/es-an.smt.cfg.sh`
- `Pipeline/sbatch/smt/fr-mfe.smt.cfg.sh`
- `Pipeline/sbatch/smt/fr-oc.smt.cfg.sh`

### `Pipeline/sh/` (2 files)
- Add `source .env` at the top and replace all hardcoded paths with `${CHARLOTTE_HOME}` and `${DATA_HOME}`.

Files:
- `Pipeline/sh/conduct_hyperparam_search_space.sh`
- `Pipeline/sh/compile_hyperparam_search_results.sh`

---

## 7. README — complete incomplete sections

Two sections are stubs:
- `## Environments` — the `conda create` block is empty; fill in the actual commands for creating the `char1.0` and `cop_mt` environments.
- The installation narrative is cut off mid-sentence.

---

## Summary

| Priority | Step | Files affected |
|---|---|---|
| Critical (PII) | Personal email | `Pipeline/write_scripts.py`, 6 sbatch scripts |
| Critical (security) | `.env` not in `.gitignore` | `.gitignore` |
| High | Rename `HOME` → `CHARLOTTE_HOME` | `.env`, all cfg/yaml/sh files |
| High | `.cfg` files | 6 cfg files + 2 shell scripts |
| High | YAML configs + `read_config()` | 15 yaml files + `NMT/train.py` |
| High | `sys.path` fix | `Pipeline/make_SC_training_data.py` |
| Medium | Python argparse defaults | 4 Python files |
| Medium | Python hardcoded result/model paths | `NMT/hr_CopperMT.py`, `NMT/evaluate.py` |
| Medium | sbatch/sh scripts | 8 scripts |
| Low | README completion | `README.md` |
