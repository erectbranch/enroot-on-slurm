#!/bin/bash

hostname

NODE_RANK=$1
MASTER_ADDR=$2
MASTER_PORT=7000
export MASTER_ADDR=$MASTER_ADDR
export MASTER_PORT=$MASTER_PORT

. env.sh
export WORLD_SIZE=$WORLD_SIZE

torchrun --standalone \
         --nnodes $NNODES \
         --nproc_per_node $NPROC_PER_NODE \
         --node_rank $NODE_RANK \
         --master_addr $MASTER_ADDR \
         --master_port $MASTER_PORT \
         train.py -np $NPROC_PER_NODE \
                  -n $NNODES