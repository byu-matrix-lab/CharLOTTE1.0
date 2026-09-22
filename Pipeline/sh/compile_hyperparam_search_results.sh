source .env

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate cop_mt

python Pipeline/compile_hyperparam_search_results.py \
    --COPPERMT ${DATA_HOME}/CopperMT \
    --langs es-an,fr-mfe,fr-oc,uz-kaa \
    --tag HYP_SEARCH > Pipeline/sh/compile_hyperparam_search_results.out

