source .env

echo "Removing rnn_hyperparams"
rm Pipeline/rnn_hyperparams/*.txt
rm Pipeline/rnn_hyperparams/manifest.json

echo "Removing sbatch files"
rm Pipeline/sbatch/hyper_param_search/*

echo "Removing cfgs"
rm -r Pipeline/cfg/SC-HYPERPARAM_SEARCH

echo "Removing slurm outputs"
rm Pipeline/slurm_outputs/hyper_param_search_outputs/*
rm Pipeline/slurm_outputs/hyper_param_search_outputs_/*

echo "Removing smt slurm outputs"
rm Pipeline/slurm_outputs/SC_smt/*

echo "Removing parameters"
rm Pipeline/parameters/*ES-AN*
rm Pipeline/parameters/*FR-MFE*
rm Pipeline/parameters/*FR-OC*


echo "Removing CoppertMT lang subdirs"
rm -r ${DATA_HOME}/CopperMT/ES_*
rm -r ${DATA_HOME}/CopperMT/FR_*

echo "Removing COGNATE_TRAIN lang subdirs"
rm -r ${DATA_HOME}/data/COGNATE_TRAIN/es-*
rm -r ${DATA_HOME}/data/COGNATE_TRAIN/fr-*

# echo "ONLY DELETED FILES AND DIRS"
# exit

python Pipeline/make_hyperparam_search_space.py \
    --cfgs Pipeline/cfg/SC/fr-mfe.cfg,Pipeline/cfg/SC/es-an.cfg,Pipeline/cfg/SC/bn-as.cfg,Pipeline/cfg/SC/bho-hi.cfg,Pipeline/cfg/SC/djk-en.cfg,Pipeline/cfg/SC/ewe-fon.cfg,Pipeline/cfg/SC/fon-ewe.cfg,Pipeline/cfg/SC/hi-bho.cfg,Pipeline/cfg/SC/lua-bem.cfg,Pipeline/cfg/SC/en-djk.ATT.cfg,Pipeline/cfg/SC/ar-aeb.cfg,Pipeline/cfg/SC/ar-apc.cfg

# echo "CREATED SEARCH SPACE BUT DID NOT RUN"
# exit

echo "RNN SBATCH:-"
for f in Pipeline/sbatch/hyper_param_search/*
do
    echo "    $f"
    sbatch $f
done

echo ""
echo "SMT SBATCH:-"
for f in Pipeline/sbatch/smt/*
do
    echo "    $f"
    sbatch $f
done