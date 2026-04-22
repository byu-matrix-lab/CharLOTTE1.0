# CharLOTTE
This is the codebase for **CharLOTTE:** (**Char**acter-**L**evel **O**rthographic **T**ransfer for **T**ranslation **E**nhancement), a system for enhancing knowledge transfer from a high to a low-resource language in NMT by leveraging orthographic correspondence patterns.

See our [paper], referenced below, for an explanation of the method.

# Installation
This codebase uses and expects *Conda* environments. The *setup.sh* assumes Conda is already installed and will create two environments `char1.0` and `cop_mt`. It will also install the [CopperMT](https://github.com/clefourrier/CopperMT), [Fast Align](https://github.com/clab/fast_align), and [BYU Matrix Data Cleaning Pipeline](https://github.com/byu-matrix-lab/data-cleaning-pipeline) codebases.
```
bash setup.sh
```

# Experiments
To create the OC training scripts, run:
```
bash Pipeline/sh/conduct_hyperparam_search_space.sh
```
This will ONLY create the training scripts for each OC model in the hyperparameter search space. See below to run the selected models reported in our paper.

If you actually want to run the hyperparameter search yourself using an HPC cluster, run this instead:
```
bash Pipeline/sh/conduct_hyperparam_search_space.sh run
```
> **_NOTE:_** To edit the SBATCH parameters used, edit the SBATCH_TEMPLATE string in Pipeline/make_hyperparam_search_space.py

## es/an --> en
### Train OC Model
```
bash Pipeline/train_SC.sh Pipeline/cfg/SC-HYPERPARAM_SEARCH/es-an.213.cfg
```

If running on an HPC cluster, run this instead:
```
sbatch Pipeline/sbatch/hyperparam_search/es-an.213.cfg.sh
```
> **_NOTE:_** You may need to edit the SBATCH parameters in the file referenced above.

### Reshape Parent Language

### Train NMT Tokenizer

### Train NMT Model

### NMT Inference


## fr/mfe --> en
### Train OC Model

### Reshape Parent Language

### Train NMT Tokenizer

### Train NMT Model

### NMT Inference


## fr/oc --> en
### Train OC Model

### Reshape Parent Language

### Train NMT Tokenizer

### Train NMT Model

### NMT Inference
