# https://pytorch.org/tutorials/intermediate/ddp_tutorial.html
import os
import torch
import torch.distributed as dist
import torch.nn as nn
import torch.optim as optim

from torch.nn.parallel import DistributedDataParallel as DDP

class ToyModel(nn.Module):
    def __init__(self):
        super(ToyModel, self).__init__()
        self.net1 = nn.Linear(10, 10)
        self.relu = nn.ReLU()
        self.net2 = nn.Linear(10, 5)

    def forward(self, x):
        return self.net2(self.relu(self.net1(x)))


def demo_basic():
    device_id = int(os.environ["LOCAL_RANK"])
    torch.cuda.set_device(device_id)

    # 1. get the world size and rank from environment variables
    world_size = int(os.getenv('WORLD_SIZE', '1'))
    rank = int(os.getenv('RANK', '0'))

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
    torch.distributed.barrier()

    model = ToyModel().to(device_id)
    ddp_model = DDP(model, device_ids=[device_id])
    loss_fn = nn.MSELoss()
    optimizer = optim.SGD(ddp_model.parameters(), lr=0.001)

    optimizer.zero_grad()
    outputs = ddp_model(torch.randn(20, 10))
    labels = torch.randn(20, 5).to(device_id)
    loss_fn(outputs, labels).backward()
    optimizer.step()
    dist.destroy_process_group()
    
    print(f"Finished running basic DDP example on rank {rank}.")

if __name__ == "__main__":
    demo_basic()
