import argparse
import hashlib
import os
import time
import torch

from pathlib import Path
from typing import Dict

__all__ = [
    "get_mem_stats",
    "get_wandb_config",
    "LocalTimer",
]

def get_mem_stats(device=None):
    mem = torch.cuda.memory_stats(device)
    props = torch.cuda.get_device_properties(device)
    return {
        "total_gb": 1e-9 * props.total_memory,
        "curr_alloc_gb": 1e-9 * mem["allocated_bytes.all.current"],
        "peak_alloc_gb": 1e-9 * mem["allocated_bytes.all.peak"],
        "curr_resv_gb": 1e-9 * mem["reserved_bytes.all.current"],
        "peak_resv_gb": 1e-9 * mem["reserved_bytes.all.peak"],
    }


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


class LocalTimer:
    def __init__(self, device: torch.device):
        if device.type == "cpu":
            self.synchronize = lambda: torch.cpu.synchronize(device=device)
        elif device.type == "cuda":
            self.synchronize = lambda: torch.cuda.synchronize(device=device)
        self.measurements = []
        self.start_time = None

    def __enter__(self):
        self.synchronize()
        self.start_time = time.time()
        return self

    def __exit__(self, type, value, traceback):
        if traceback is None:
            self.synchronize()
            end_time = time.time()
            self.measurements.append(end_time - self.start_time)
        self.start_time = None

    def avg_elapsed_ms(self):
        return 1000 * (sum(self.measurements) / len(self.measurements))

    def reset(self):
        self.measurements = []
        self.start_time = None
