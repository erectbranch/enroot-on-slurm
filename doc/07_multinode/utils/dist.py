import os
import torch

from contextlib import contextmanager

__all__ = [
    "dist_init", 
    "get_rank", 
    "get_local_rank",
    "get_world_size",
    "is_master", 
    "is_dist_initialized", 
    "dist_barrier",
    "rank0_first",
]

def dist_init() -> None:
    # 1. get the local rank and rank from environment variables
    local_rank = int(os.environ["LOCAL_RANK"])
    rank = int(os.getenv('RANK', '0'))
    world_size = int(os.getenv('WORLD_SIZE', '1'))

    # 2. define the init method
    init_method = 'tcp://'
    master_ip   = os.getenv('MASTER_ADDR', 'localhost')    # os.getenv(key, default)
    master_port = os.getenv('MASTER_PORT', '8000')
    init_method += master_ip + ':' + master_port

    # 3. initialize the process group
    torch.distributed.init_process_group(
        backend="nccl",
        world_size=world_size,
        rank=rank,
        init_method=init_method,
    )
    torch.cuda.set_device(local_rank)
    torch.distributed.barrier()

def get_rank() -> int:
    return int(os.environ["RANK"])

def get_local_rank() -> int:
    return int(os.environ["LOCAL_RANK"])

def get_world_size() -> int:
    return int(os.environ["WORLD_SIZE"])

def is_master() -> bool:
    return get_rank() == 0

def is_dist_initialized() -> bool:
    return torch.distributed.is_initialized()

def dist_barrier() -> None:
    if is_dist_initialized():
        torch.distributed.barrier()


@contextmanager
def rank0_first():
    rank = torch.distributed.get_rank()
    if rank == 0:
        yield
    torch.distributed.barrier()
    if rank > 0:
        yield
    torch.distributed.barrier()