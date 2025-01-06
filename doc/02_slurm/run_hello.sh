#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu4
#SBATCH --gres=gpu:a6000:1
#SBATCH -o ./%N.%j.out
#SBATCH -e ./%N.%j.err
#SBATCH --time=00:30:00

hostname                      
date                          

module add python/3.11.2

python hello.py