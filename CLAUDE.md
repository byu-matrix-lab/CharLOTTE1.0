# CLAUDE.md — CharLOTTE1.0_public

## Project overview

CharLOTTE (**Char**acter-**L**evel **O**rthographic **T**ransfer for **T**oken **E**mbeddings) is a research system for low-resource NMT that exploits character-level correspondences between related language pairs. The three language pairs used in the paper are:
- Spanish (`es`) → Aragonese (`an`)
- French (`fr`) → Occitan (`oc`)
- French (`fr`) → Morisyen (`mfe`)

## Repository structure

```
CharLOTTE1.0_public/
├── word_alignments/      # Step 1: fast_align pipeline to extract cognate pairs
├── Pipeline/             # Step 2: SC (Sound Change) model training & prediction
│   ├── cfg/SC/           # .cfg configs for RNN SC models (one per language pair)
│   ├── cfg/SC_SMT/       # .cfg configs for SMT SC models
│   ├── sbatch/           # Example SLURM job scripts
│   └── sh/               # Utility shell scripts
├── NMT/                  # Step 3: BART-based NMT training
│   ├── configs/CONFIGS/  # YAML training configs (one subdir per low-resource lang pair)
│   └── data/CharLOTTE/   # Parallel training data (PLAIN and SC-augmented)
├── CopperMT/             # SMT baseline; wraps the CopperMT library
│   └── CopperMTfiles/    # CharLOTTE-specific scripts copied into CopperMT at setup
├── setup.sh              # Environment + dependency installation
├── requirements.txt      # Dependencies for conda env `char1.0`
├── requirements.copper.txt  # Dependencies for conda env `cop_mt`
├── .env                  # Local path config (not committed — see .env.example)
└── CLEANUP_PLAN.md       # Ongoing plan for sanitizing the repo for public release
```

## Conda environments

Two environments are required and their names must match exactly:
- `char1.0` — used for word alignment, NMT training, and SC data preparation (`requirements.txt`, Python 3.10)
- `cop_mt` — used for CopperMT/fairseq SC model training (`requirements.copper.txt`, Python 3.8)

## Environment variables

Paths are configured via `.env` in the repo root. Never commit `.env` — it is gitignored. Use `.env.example` as a template.

| Variable | Purpose |
|---|---|
| `CHARLOTTE_HOME` | Absolute path to this repo root |
| `DATA_HOME` | Absolute path to external data/model storage |

Shell scripts source `.env` before sourcing `.cfg` files. Python scripts load `.env` via `python-dotenv` (or a manual loader) and then call `os.path.expandvars()` on config values. YAML config values use `${CHARLOTTE_HOME}` and `${DATA_HOME}` syntax.

## Key entry points

| Script | Purpose |
|---|---|
| `Pipeline/train_SC.sh <cfg>` | Full SC pipeline: cognate extraction → SC model training → evaluation |
| `Pipeline/pred_SC.sh <cfg>` | Apply a trained SC model to new data |
| `NMT/train.py -c <yaml> -m TRAIN` | Train a BART NMT model |
| `NMT/train.py -c <yaml> -m TEST` | Evaluate a trained NMT model (BLEU, chrF) |

All shell scripts are run from the **repo root** (`CHARLOTTE_HOME`).

## Config file formats

**`.cfg` files** (`Pipeline/cfg/`) are bash scripts sourced by `train_SC.sh` / `pred_SC.sh`. They set shell variables consumed directly by those scripts.

**YAML files** (`NMT/configs/`) are loaded by `NMT/train.py:read_config()`. String values support `${VAR}` expansion via `os.path.expandvars()`.

Config naming conventions:
- `PRETRAIN.<high-resource-pair>.yaml` — pretraining on the high-resource language pair
- `PRETRAIN.SC_<hr>2<lr>-<tgt>.yaml` — pretraining on SC-augmented data
- `FINETUNE.<high-resource-pair>>><low-resource-pair>.yaml` — fine-tuning on the low-resource pair
- `FINETUNE.SC_<hr>2<lr>-<tgt>>><lr-pair>.yaml` — fine-tuning with SC augmentation
- `NMT.<low-resource-pair>.yaml` — training directly on low-resource data (no transfer)

## Pipeline flow

```
Parallel data (CSV)
    │
    ▼
word_alignments/          ← fast_align: find aligned word pairs
    │
    ▼
Pipeline/train_SC.sh      ← extract cognates → train SC model (CopperMT/fairseq)
    │
    ▼
Pipeline/pred_SC.sh       ← apply SC model to high-resource data → SC-augmented CSVs
    │
    ▼
NMT/train.py (PRETRAIN)   ← pretrain BART on (SC-augmented) high-resource data
    │
    ▼
NMT/train.py (FINETUNE)   ← fine-tune on low-resource data
    │
    ▼
NMT/train.py (TEST)       ← evaluate: BLEU, chrF
```

## Data format

Training data is stored as `.csv` files with columns `src_lang`, `tgt_lang`, `src`, `tgt`. The `MultilingualDataset` class (`NMT/parallel_datasets.py`) reads these files and optionally filters by language pair.

SC-augmented data lives in `NMT/data/CharLOTTE/SC/` with subdirectory names like `SC_es2an-en/` (meaning: SC model trained on `es→an`, applied to `es-en` data).

## External dependencies (not in this repo)

- **fast_align** — cloned and built by `setup.sh` into `fast_align/`
- **CopperMT** — cloned by `setup.sh` into `CopperMT/CopperMT/`; CharLOTTE scripts are then copied in via `CopperMT/CopperMTfiles/copy_files.py`
- **SPM tokenizer models** — stored at `${DATA_HOME}/CognateMT/spm_models/`
- **Trained model checkpoints** — stored at `${DATA_HOME}/CognateMT/PredictCognates/`
- **COMET model** (optional, for evaluation) — path set via `COMET_MODEL_PATH` env var

## Coding conventions

- Python scripts print a banner on entry (e.g., `#### train.py ####`) and echo all arguments.
- All scripts are designed to be run from the repo root.
- `NMT/` Python modules import each other directly by name (no package `__init__.py`); the working directory or `PYTHONPATH` must include `NMT/` when running scripts outside that directory.
- Config assertions in `read_config()` enforce valid combinations of `val_interval` and `early_stop`.

## Active cleanup work

See `CLEANUP_PLAN.md` for the full plan to remove hardcoded personal paths and other issues before public release. The current state of the repo still contains references to the original private research repo (`/home/hatch5o6/Cognate/code/`) that are being systematically replaced.
