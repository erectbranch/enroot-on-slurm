#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu4
#SBATCH --gres=gpu:a6000:1
#SBATCH -o ./jupyter.%N.%j.out
#SBATCH -e ./jupyter.%N.%j.err
#SBATCH --time=00:30:00

# module unload cuda/11.2.2
# module load cuda/11.8.0

gate_node='gate2'

user=`whoami`
gate_port=`python -c 'import socket; s = socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close();'`
ssh -T $user@$gate_node
node_port=`python -c 'import socket; s = socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close();'`
ssh -T $user@$gate_node -R $gate_port:localhost:$node_port -fN "while sleep 100; do; done"&

echo "start at:" `date`
echo "node_port: $node_port"
echo "gate_port: $gate_port"

python -m jupyter lab $HOME \
        --ip=0.0.0.0 \
        --port $node_port \
        --allow-root \
        --no-browser