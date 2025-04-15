#!/bin/bash

CPUS_PER_TASK=8
GRES="gpu:a6000:4"
CONTAINER_NAME="my-torch"

NNODES=2
NPROC_PER_NODE=4
WORLD_SIZE=$((NPROC_PER_NODE * NNODES))

# container settings to be used with enroot create
CONTAINER_NAME="my-torch"
CONTAINER_IMAGE="$HOME/nvidia+pytorch+24.06-py3.sqsh"

# enroot runtime settings
REMOVE_ENROOT_CACHE=false
MY_UID=`id -u`
CONTAINER_CACHE_DIR="/enroot/$MY_UID/data/$CONTAINER_NAME"    # enroot.conf