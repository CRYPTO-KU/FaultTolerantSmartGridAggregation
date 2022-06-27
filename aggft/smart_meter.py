from abc import ABC, abstractmethod
from typing import Any

from data_concentrator import DC

class SM(ABC):

    # Constructor

    def __init__(self):
        pass

    # Getters

    # Abstract Methods

    @abstractmethod
    def send_initial_msg(self) -> Any:
        pass

    # Protocol Implementation

    def round_initial_activation(self):
        self.send_initial_msg()

    def round_final_activation(self):
        pass
