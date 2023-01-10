import json

from dataclasses import dataclass
from queue       import Queue

from abc         import ABC, abstractmethod
from typing      import Dict, Tuple

################################################################################
# Data Types
################################################################################

Host = str
Port = int

@dataclass(frozen = True)
class Address:
    host : Host
    port : Port
    valid: bool

################################################################################
# Actual Networking
################################################################################

# Keywords that mark the beginning and ending of a network request
_DATA_BEG_MARK = "<BEG>"
_DATA_END_MARK = "<END>"

class NetworkManager(ABC):
    @abstractmethod
    def bind(self, address: Address) -> Queue:
        pass

    @abstractmethod
    def send(self, address: Address, data: str, timeout: float) -> bool:
        pass

    @abstractmethod
    def listen(self) -> None:
        pass

################################################################################
# Shared Memory Networking
################################################################################

class SharedMemoryNetworkManager(NetworkManager):
    def __init__(self, address: Address, registry: Dict[Tuple[Host, Port], Queue]):
        self.address  = address
        self.registry = registry

    def bind(self, _):
        return

    def send(self, address: Address, data: str, _) -> bool:
        if address.valid:
            self.registry[(address.host, address.port)].put(json.loads(data))
            return True
        return False

    def listen(self) -> Queue:
        return self.registry[(self.address.host, self.address.port)]
