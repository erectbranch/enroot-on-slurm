#!/bin/bash

NODE_RANK=$1
MASTER_ADDR=$2
SLURM_JOB_ID=$3

pip install --default-timeout=100 wandb
pip install --default-timeout=100 tqdm
pip install --default-timeout=100 datasets
pip install --default-timeout=100 transformers

# Notes: You need to set WANDB_API_KEY in login.sh
. login.sh
. env.sh

# Must be modified to your own project
WANDB_ENTITY="{your-wandb-entity}"
WANDB_PROJECT="{your-wandb-project}"
SAVE_DIR=".exp/enroot-on-slurm"
EXPERIMENT_NAME="gpt2-alpaca"

export WANDB_ENTITY=$WANDB_ENTITY
export WANDB_PROJECT=$WANDB_PROJECT

# Set the master address and port
export SLURM_JOB_ID=$SLURM_JOB_ID
MASTER_PORT=$(expr 5000 + $(echo -n ${SLURM_JOB_ID} | tail -c 4))
export MASTER_ADDR=$MASTER_ADDR
export MASTER_PORT=$MASTER_PORT
export WORLD_SIZE=$WORLD_SIZE

export OMP_NUM_THREADS=1

torchrun --nnodes $NNODES \
         --nproc_per_node $NPROC_PER_NODE \
         --node_rank $NODE_RANK \
         --master_addr $MASTER_ADDR \
         --master_port $MASTER_PORT \
         train_llm.py  \
         -e $EXPERIMENT_NAME \
         -d tatsu-lab/alpaca \
         -m openai-community/gpt2 \
         --save-dir $SAVE_DIR 