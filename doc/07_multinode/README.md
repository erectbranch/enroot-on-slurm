# 7 Multi-node LLM Training with Wandb

> [Weights & Biases](https://wandb.ai/site/)

---

## 7.1 Wandb

<h3 align="center">
  <p align="center">
  
  ![wandb logo](../../images/wandb.png)
  
  </p>
</h1>

**Wandb** is a tool for tracking and visualizing machine learning experiments. 

---

### 7.1.1 Wandb Authentication

> **Note**: You need to authenticate your Wandb account before using it. (https://wandb.ai/authorize)

(1) Add the Wandb API key to your environment variables. Then, paste the API key into the Wandb login script. (`login.sh`)

```bash
# login.sh
export WANDB_API_KEY="{your-api-key}"

wandb login $WANDB_API_KEY
```

(2) Install the Wandb library and set up the Wandb environment.

```bash
# torchrun.sh
pip install wandb
. login.sh

# Must be modified to your own project
WANDB_ENTITY="{your-wandb-entity}"
WANDB_PROJECT="{your-wandb-project}"
SAVE_DIR="{your-save-dir}"
EXPERIMENT_NAME="{your-experiment-name}"
```

---

### 7.1.2 Wandb Environment Variables

> [Weights & Biases: init](https://docs.wandb.ai/ref/python/init/)

The Wandb environment variables are used to set up the `wandb.init()` function.

```python
# utils/log.py
def get_wandb_config(args: argparse.Namespace) -> Dict[str, str]:
    exp_dir: Path = Path(args.save_dir) / args.experiment_name
    exp_dir = str(exp_dir)

    return {
        "entity": os.environ.get("WANDB_ENTITY", None),
        "project": os.environ.get("WANDB_PROJECT", "enroot-on-slurm"),
        "name": args.experiment_name,
        "id": hashlib.sha1(exp_dir.encode("utf-8")).hexdigest(),
        "resume": "allow",
        "tags": [args.model_name, args.dataset_name],
    }
```

The `get_wandb_config()` function is used to set up the `wandb.init()` arguments.

| Argument | Variable | Description |
| --- | --- | --- |
| `entity` | `$WANDB_ENTITY` | The Wandb username or team name. <br>(c.f., you can find it in the [Wandb settings](https://wandb.ai/settings) "Default team").
| `project` | `$WANDB_PROJECT` | The Wandb project name. |
| `name` | `$EXPERIMENT_NAME` | A short display name for the run.<br>(e.g., `gpt2_lr_3e-5_bs_1_epochs_100`) |
| `id` | SHA1(`$SAVE_DIR`/`$EXPERIMENT_NAME`) | A unique identifier for the run.<br>**If used for resuming a run**, **it should be the same as the original run**. |

---

### 7.1.3 Wandb Initialization

> [Weights & Biases: Log distributed training experiments](https://docs.wandb.ai/guides/track/log/distributed-training/)

These arguments are passed to the `wandb.init()` function to initialize the Wandb run. In distributed training, only the master process (rank 0) should call `wandb.init()`.

```python
# train_llm.py
if int(os.environ["RANK"])==0:
    wandb.init(
        **get_wandb_config(args),
        config={
            "args": vars(args),
            "training_data_size": len(train_data),
            "num_batches": len(dataloader),
            "world_size": world_size,
        },
    )
```

---

## 7.2 Multi-node LLM Training

> [Hugging Face: openai-community/gpt2](https://huggingface.co/openai-community/gpt2)

In this section, we will train a small version of the **GPT-2** model on multiple nodes using the Wandb library for logging and tracking. The model is the smallest version of the GPT-2 model, with **124M** parameters.

- Requirements: 
  - **wandb**
  - **tqdm**
  - **datasets**
  - **transformers**

---

### 7.2.1 Setup Environment Variables (env.sh)

In the `env.sh` file, we will set up the environment variables for the multi-node training. The `NNODES` variable is used to specify the number of nodes to be used for training. 

In this example, we will allocate 2 nodes with 4 GPUs each, for a total of 8 GPUs.

```bash
# env.sh
CPUS_PER_TASK=8
GRES="gpu:a6000:4"

NNODES=2
NPROC_PER_NODE=4
WORLD_SIZE=$((NPROC_PER_NODE * NNODES))
```

---

### 7.2.2 Slurm Job Script (run_script.sh)

Then, we will set up the Slurm environment variables for the multi-node training. (`run_script.sh`)

```bash
# run_script.sh
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu4
#SBATCH --gres=gpu:a6000:4
#SBATCH -o ./wandb.%N.%j.out
#SBATCH -e ./wandb.%N.%j.err
#SBATCH --cpus-per-task=8
...
```

---

### 7.2.3 torchrun Script (torchrun.sh)

We will use the `torchrun` command to launch the training script on multiple nodes. 

```bash
# torchrun.sh
...
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
```

---

## 7.3 Run the Experiment

> [Hugging Face: Environment variables](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables)

To run the experiment, you need to submit the job script to the Slurm scheduler.

```bash
# Run the script
$ sbatch run_script.sh
```

The Hugging Face `transformers` and `datasets` libraries will download the model and dataset automatically to `$HF_HOME`. (default: `~/.cache/huggingface`)

---