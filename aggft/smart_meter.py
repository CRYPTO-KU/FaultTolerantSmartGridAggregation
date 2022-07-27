from abc import ABC, abstractmethod
import copy
from typing import Any
from sortedcontainers import SortedSet

from data_concentrator import DC
from types.url import URL
from typing import Any, Dict, List, Tuple

class SM(ABC):

    # Constructor

    def __init__(self, id: int, dc_address: URL, sm_addresses: List[str],
                 n_min: int, epoch_seconds: float, round_seconds: float):

        # Addresses of environment devices
        self._id = id
        self._dc_address = dc_address
        self._sm_addresses = sm_addresses
        self._n_min = n_min

        # Timouts
        self._t_epoch = epoch_seconds
        self._t_round = round_seconds

        # State
        self._round = -1

    # Getters

    @property
    def id(self) -> int:
        """Smart meter id."""
        return self._id

    @property
    def dc_address(self) -> URL:
        """Data concentrator address."""
        return self._dc_address

    @property
    def sm_addresses(self) -> List[str]:
        """Smart meters addresses."""
        return copy.deepcopy(self._sm_addresses)

    @property
    def n_min(self) -> int:
        """Minimum number of smart meters participating in a round."""
        return self._n_min

    @property
    def epoch(self) -> float:
        """Time at which the system started, in epoch seconds."""
        return self._t_epoch

    @property
    def round_duration(self) -> float:
        """Duration of a single round in seconds."""
        return self._t_round

    @property
    def current_round(self) -> int:
        """Index of the current round (zero-based)."""
        return self._round

    # Abstract Methods

    @abstractmethod
    def send_initial_msg(self) -> Any:
        pass

    # Protocol Implementation

    def round_initial_activation(self):
        self.send_initial_msg()

    def round_final_activation(self):
        pass

    @abstractmethod
    async def _send_final_message(self, l_act: SortedSet, s_final: int) -> None:
        pass

    def _is_last(self, l_rem: SortedSet, l_act: SortedSet):
        return len(l_rem) == 0 or len(l_rem) + len(l_act) < self.n_min
