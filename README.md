# CharLOTTE
This is the codebase for **CharLOTTE:** (**Char**acter-**L**evel **O**rthographic **T**ransfer for **T**ranslation **E**nhancement), a system for enhancing knowledge transfer from a high to a low-resource language in NMT by leveraging orthographic correspondence patterns.

See our [paper], referenced below, for an explanation of the method.

This repository was tested on **Red Hat Enterprise Linux 9.6 (Plow)**.

> **_NOTE:_** We provide documentation for the option of running parts of the pipeline on an HPC cluster. You may need to edit the SBATCH parameters of the respective bash scripts to configure your qos, gpus, memory, etc.

# Installation
This codebase uses and expects *Conda* environments. The *setup.sh* assumes Conda is already installed and will create two environments `char1.0` and `cop_mt`. It will also install the [CopperMT](https://github.com/clefourrier/CopperMT), [Fast Align](https://github.com/clab/fast_align), and [BYU Matrix Data Cleaning Pipeline](https://github.com/byu-matrix-lab/data-cleaning-pipeline) codebases.
```
bash setup.sh
```

# Downloading and Preparing Data
**Download and clean data**

Not on HPC:
```
bash data/prepare_data.sh
```
On HPC:
```
bash data/prepare_data_sbatch.sh
```
> **_NOTE:_** edit SBATCH parameters in *data/clean_data_sbatch.sh* (called from *prepare_data_sbatch*) as needed.

**Once data is downloaded and cleaned, make the datasets**

Not on HPC:
```
bash data/make_training_data.sh
```
On HPC:
```
sbatch data/make_training_data_sbatch.sh
```
> **_NOTE:_** edit SBATCH parameters in *data/make_training_data_sbatch.sh* as needed.


# Experiments

To create the OC training scripts, run:
```
bash Pipeline/sh/conduct_hyperparam_search_space.sh
```
This will ONLY create the training scripts for each OC model in the hyperparameter search space. Continue on to section **CharLOTTE and Baseline Pipelines** to train and run the selected models reported in our paper.

If you actually want to run the OC hyperparameter search yourself using an HPC cluster, run this instead:
```
bash Pipeline/sh/conduct_hyperparam_search_space.sh run
```
> **_NOTE:_** To edit the SBATCH parameters used, edit the **SBATCH_TEMPLATE** string in *Pipeline/make_hyperparam_search_space.py*.

Then compile the results for the hyperparameter search:
```
bash Pipeline/sh/compile_hyperparam_search_results.sh
```
The results will appear in *Pipeline/hyperparam_search_results*



## CharLOTTE and Baseline Pipelines
The documentation will demonstrate how to reproduce our results for the *es/an→en* scenario, with notes on how to run the *fr/mfe→en*, *fr/oc→en*, and *uz/kaa→en* scenarios.

### Train OC Model
For the *fr/mfe→en* scenario, replace *"es-an.213.cfg"* with *"fr-mfe.102.cfg"*

For the *fr/oc→en* scenario, replace *"es-an.213.cfg"* with *"fr-oc.251.cfg"*

For the *uz/kaa→en* scenario, replace *"es-an.213.cfg"* with *"uz-kaa.264.cfg"*

Not on HPC:
```
bash Pipeline/train_SC.sh Pipeline/cfg/SC-HYPERPARAM_SEARCH/es-an.213.cfg
```

On HPC:
```
sbatch Pipeline/sbatch/hyperparam_search/es-an.213.cfg.sh
```
> **_NOTE:_** You may need to edit the SBATCH parameters in the file referenced above.

### Reshape Parent Language
For the *fr/mfe→en* scenario, replace *"es-an.213.cfg"* with *"fr-mfe.102.cfg"*

For the *fr/oc→en* scenario, replace *"es-an.213.cfg"* with *"fr-oc.251.cfg"*

For the *uz/kaa→en* scenario, replace *"es-an.213.cfg"* with *"uz-kaa.264.cfg"*

Not on HPC:
```
bash Pipeline/pred_SC.sh Pipeline/cfg/SC-HYPERPARAM_SEARCH/es-an.213.cfg
```

On HPC:
```
sbatch Pipeline/sbatch/predict/es-an.213.cfg.sh
```

> **_NOTE:_** You may need to edit the SBATCH parameters in the file referenced above.

### OC Model Characterization ###
To run the OC N-Gram Correspondence Characterization on a single language pair:

```
bash Ngram_Correspondences/sh/es-an.sh
```
For the *fr/mfe→en* scenario, replace *"es-an.sh"* with *"fr-mfe.sh"*

For the *fr/oc→en* scenario, replace *"es-an.sh"* with *"fr-oc.sh"*

For the *uz/kaa→en* scenario, replace *"es-an.sh"* with *"uz-kaa.sh"*


To run on all 4 language pairs at once:
```
bash Ngram_Correspondences/sh/all.sh
```

### Train NMT Tokenizers
**Tokenizers for transfer learning and simple baseline NMT models:**

For the *fr/mfe→en* scenario, replace *"es-an_en"* with *"fr-mfe_en"*

For the *fr/oc→en* scenario, replace *"es-an_en"* with *"fr-oc_en"*

For the *uz/kaa→en* scenario, replace *"es-an_en"* with *"uz-kaa_en"*

```
bash Pipeline/train_srctgt_tokenizer.sh Pipeline/cfg/tok/es-an_en.cfg
```

**Tokenizer for CharLOTTE NMT model:**

For the *fr/mfe→en* scenario, replace *"es2an-an_en"* with *"fr2mfe-mfe_en"*

For the *fr/oc→en* scenario, replace *"es2an-an_en"* with *"fr2oc-oc_en"*

For the *uz/kaa→en* scenario, replace *"es2an-an_en"* with *"uz2kaa-kaa_en"*

```
bash Pipeline/train_srctgt_tokenizer.sh Pipeline/cfg/tok/es2an-an_en.cfg
```

**You can also optionally train all tokenizers at once by running *Pipeline/train_all_tokenizers.sh*:**

Not on HPC:
```
bash Pipeline/train_all_tokenizers.sh
```

On HPC:
```
sbatch Pipeline/train_all_tokenizers.sh
```
> **_NOTE:_** You may need to edit the SBATCH parameters in the file referenced above.


### NMT Training and Testing
First, make the training scripts with *NMT/make_sbatch.py*:

You can optionally include your qos with the --qos flag if you intend to train on an HPC cluster.
```
python NMT/make_sbatch.py [--qos {your qos}]
```
> **_NOTE:_** You may edit the **sbatch_template** string in *NMT/make_sbatch.py*  to accomodate for your HPC resources as needed.

The following scripts should now be created. They were written to run on an HPC cluster. The scripts themselves make the sbatch commands, so you will simply invoke them with "bash". If not running on an HPC cluster, simply edit the scripts, replacing "sbatch" with "bash".

For the *fr/mfe→en* scenario, replace *"an-en"* in each of the script paths below with *"mfe-en"*

For the *fr/oc→en* scenario, replace *"an-en"* in each of the script paths below with *"oc-en"*

For the *uz/kaa→en* scenario, replace *"an-en"* in each of the script paths below with *"kaa-en"*

##### Simple baseline model
Train:
```
bash NMT/sbatch/TRAIN/an-en/all_NMT.sh
```

Then when done, test:
```
bash NMT/sbatch/TEST/an-en/all_NMT.sh
```

##### Transfer learning baseline and CharLOTTE models
Pre-train both the CharLOTTE and baseline parent models:
```
bash NMT/sbatch/TRAIN/an-en/all_PRETRAIN.sh
```

When done, run testing on the pre-trained models. You MUST do this before fine-tuning since it will evaluate the pre-trained models on their respective validation sets so that the training script knows which pre-trained checkpoint to select for fine-tuning:
```
bash NMT/sbatch/TEST/an-en/all_PRETRAIN.sh
```

When done, fine-tune both the CharLOTTE and baseline child models:
```
bash NMT/sbatch/TRAIN/an-en/all_FINETUNE.sh
```

When done, test the child models:
```
bash NMT/sbatch/TEST/an-en/all_FINETUNE.sh
```

#### Reverse translation directions
To train the NMT models that translate into the low-resource directions, i.e. *en→es/an*, *en→fr/mfe*, *en→fr/oc*, *en→uz/kaa* you will do the same but with different paths:

##### Simple baseline model
Train:
```
bash NMT/sbatch/TRAIN.REVERSE_SRC_TGT/an-en.REVERSE_SRC_TGT/all_NMT.sh
```

Then when done, test:
```
bash NMT/sbatch/TEST.REVERSE_SRC_TGT/an-en.REVERSE_SRC_TGT/all_NMT.sh
```

##### Transfer learning baseline and CharLOTTE models
Pre-train both the CharLOTTE and baseline parent models:
```
bash NMT/sbatch/TRAIN.REVERSE_SRC_TGT/an-en.REVERSE_SRC_TGT/all_PRETRAIN.sh
```

When done, run testing on the pre-trained models. You MUST do this before fine-tuning since it will evaluate the pre-trained models on their respective validation sets so that the training script knows which pre-trained checkpoint to select for fine-tuning:
```
bash NMT/sbatch/TEST.REVERSE_SRC_TGT/an-en.REVERSE_SRC_TGT/all_PRETRAIN.sh
```

When done, fine-tune both the CharLOTTE and baseline child models:
```
bash NMT/sbatch/TRAIN.REVERSE_SRC_TGT/an-en.REVERSE_SRC_TGT/all_FINETUNE.sh
```

When done, test the child models:
```
bash NMT/sbatch/TEST.REVERSE_SRC_TGT/an-en.REVERSE_SRC_TGT/all_FINETUNE.sh
```

# Compile Scores
Compile scores for all NMT Models:
```
bash NMT/compile_results.sh
```
Scores will be written to NMT_results.txt

# Meaningful Mappings
Get the meaningful mappings data used to characterize the OC models:
```
bash Ngram_Correspondences/sh/all.sh
```
To run for a single language scenario (replace *"es-an"* with the desired language pair):
```
bash Ngram_Correspondences/sh/es-an.sh
```

Scores will be written to Ngram_Correspondences/results.xlsx