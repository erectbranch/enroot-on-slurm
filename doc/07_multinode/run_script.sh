#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu4
#SBATCH --gres=gpu:a6000:4
#SBATCH -o ./wandb.%N.%j.out
#SBATCH -e ./wandb.%N.%j.err
#SBATCH --cpus-per-task=8
#SBATCH --time=48:00:00

# 1. import $NPROC_PER_NODE, $NNODES, $WORLD_SIZE, $GRES, $CONTAINER_NAME, $CPUS_PER_TASK
. env.sh

# 2. get $MASTER_ADDR
function get_master_address(){
    NODE_LIST=`scontrol show hostnames $SLURM_JOB_NODELIST`
    MASTER_HOST=`echo $NODE_LIST | awk '{print $1}'`
    MASTER_ADDR=`cat /etc/hosts | grep $MASTER_HOST | awk '{print $1}'`
}
get_master_address
echo MASTER_ADDR:$MASTER_ADDR

# 3. locate torchrun.sh script (in the container filesystem)
ENROOT_SCRIPT=" cd /workspace/mnt && \
                bash torchrun.sh"

# 4. define the enroot initialization script
INIT_CONTAINER_SCRIPT=$(cat <<EOF

    if $REMOVE_ENROOT_CACHE ; then
        rm -rf $CONTAINER_CACHE_DIR
    fi

    if [ -d "$CONTAINER_CACHE_DIR" ] ; then 
        echo "container exist";
    else
        enroot create -n $CONTAINER_NAME $CONTAINER_IMAGE ;
    fi

EOF
)

# 5. define the script to be run by srun
SRUN_SCRIPT=$(cat <<EOF
    $INIT_CONTAINER_SCRIPT
    
    NODE_LIST=\`scontrol show hostnames \$SLURM_JOB_NODELIST\`
    node_array=(\$NODE_LIST)
    length=\${#node_array[@]}
    hostnode=\`hostname -s\`
    for (( index = 0; index < length ; index++ )); do
        node=\${node_array[\$index]}
        if [ \$node == \$hostnode ]; then
            NODE_RANK=\$index
        fi
    done 

    enroot start --root --rw \
                --mount $HOME:/workspace/mnt \
                $CONTAINER_NAME \
                bash -c "$ENROOT_SCRIPT \$NODE_RANK $MASTER_ADDR $SLURM_JOB_ID"
EOF
)

# 6. run the script with srun
mkdir -p ./log/$SLURM_JOB_ID

srun --partition=$SLURM_JOB_PARTITION \
      --gres=$GRES \
      --cpus-per-task=$CPUS_PER_TASK \
      -o ./log/%j/%N.out \
      -e ./log/%j/%N.err \
      bash -c "$SRUN_SCRIPT"
