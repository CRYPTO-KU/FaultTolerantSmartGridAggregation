from queue import Queue

from util import network

################################################################################
# Helper Functions
################################################################################


def make_registry(sm_count: int) -> network.Registry:
    registry = {}
    for i in [-1] + list(range(sm_count)):
        registry[("localhost", i)] = Queue()
    return registry
