# https://pytorch.org/tutorials/intermediate/ddp_tutorial.html
import os
import torch
import torch.distributed as dist
import torch.nn as nn
import torch.optim as optim

from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed.elastic.multiprocessing.errors import record

class ToyModel(nn.Module):
    def __init__(self):
        super(ToyModel, self).__init__()
        self.net1 = nn.Linear(10, 10)
        self.relu = nn.ReLU()
        self.net2 = nn.Linear(10, 5)

    def forward(self, x):
        return self.net2(self.relu(self.net1(x)))

@record
def main():
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
    dist.init_process_group(
        backend="nccl",
        world_size=world_size,
        rank=rank,
        init_method=init_method,
    )
    torch.cuda.set_device(local_rank)
    dist.barrier()

    DEVICE = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    model = ToyModel().to(DEVICE)
    ddp_model = DDP(model, device_ids=[local_rank], output_device=rank)
    loss_fn = nn.MSELoss()
    optimizer = optim.SGD(ddp_model.parameters(), lr=0.001)

    optimizer.zero_grad()
    outputs = ddp_model(torch.randn(20, 10))
    labels = torch.randn(20, 5).to(DEVICE)
    loss_fn(outputs, labels).backward()
    optimizer.step()
    dist.destroy_process_group()
    
    print(f"Finished running basic DDP example on rank {rank}.")

if __name__ == "__main__":
    main()
