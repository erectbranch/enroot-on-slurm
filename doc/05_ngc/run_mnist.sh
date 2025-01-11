#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu4
#SBATCH --gres=gpu:a6000:1
#SBATCH -o ./jupyter.%N.%j.out
#SBATCH -e ./jupyter.%N.%j.err
#SBATCH --time=02:00:00

hostname                      
date

CONTAINER_NAME="my-torch"

enroot start --root --rw \
    --mount $HOME:/workspace/mnt \
    $CONTAINER_NAME \
    /bin/bash -c "cd /workspace/mnt && python3 mnist.py"