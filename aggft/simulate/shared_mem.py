from queue  import Queue

from util   import network

from typing import Tuple, Dict

################################################################################
# Helper Functions
################################################################################

def make_shared_memory_net_mngr(sm_count: int) -> network.SharedMemoryNetworkManager:
    registry = {}
    for i in [-1] + list(range(sm_count)):
        registry[("localhost", i)] = Queue()
    return network.SharedMemoryNetworkManager(registry)
