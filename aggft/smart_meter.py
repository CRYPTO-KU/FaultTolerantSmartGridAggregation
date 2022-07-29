from abc import ABC, abstractmethod
from util import time
import copy
from typing import Any
from sortedcontainers import SortedSet
from util.timeoutable_coroutine import TimeoutableCoroutine

from data_concentrator import DC
from types.url import URL
from typing import Any, Dict, List, Tuple
import asyncio

class SM(ABC):

    # Constructor

    def __init__(self, id: int, dc_address: str, sm_addresses: List[str],
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

    # Public Interface

    ## Entry Point

    @abstractmethod
    def _get_server(self) -> TimeoutableCoroutine[Tuple[SortedSet, SortedSet, int]]:
        pass

    def time_until_next_round(self):
        next_round_start = self.epoch + (self.current_round + 1) * self.round_duration
        return time.remaining_until(next_round_start)

    @abstractmethod
    def _update_s(self, s: int, si: int) -> int:
        pass

    async def run(self) -> None:
        while True:
            await asyncio.sleep(self.time_until_next_round())
            self._update_round()
            si = self._get_si(self.current_round)
            await self._initial_activation(self.current_round, si)
            l_rem, l_act, s = await self._get_server().run(
                timeout = self.time_until_next_round(),
                round = round
            )
            s_new = self._update_s(s, si)
            await self._final_activation(self.current_round, l_rem, l_act, s_new)

    # Getters

    @property
    def id(self) -> int:
        """Smart meter id."""
        return self._id

    @property
    def dc_address(self) -> str:
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
    async def _send_msg(self, to: str, data: Dict[str, Any]) -> bool:
        pass

    async def _send_msg_to_dc(self, data: Dict[str, Any]) -> bool:
        return await self._send_msg(self.dc_address, data)

    async def _send_msg_to_sm(self, id: int, data: Dict[str, Any]) -> bool:
        return await self._send_msg(self.sm_addresses[id], data)

    @abstractmethod
    def _get_si(self, round: int) -> int:
        pass

    @abstractmethod
    def _get_initial_msg(self, round: int, si: int) -> Dict[str, Any]:
        pass

    async def _initial_activation(self, round: int, si: int):
        initial_msg = self._get_initial_msg(round, si)
        await self._send_msg_to_dc(initial_msg)

    @abstractmethod
    def _get_middle_msg(self, round: int, l_rem: SortedSet, l_act: SortedSet, s_current: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_final_msg(self, round: int, l_act: SortedSet, s: int) -> Dict[str, Any]:
        pass

    async def _final_activation(self, round: int, l_rem: SortedSet, l_act: SortedSet, s_current: int):
        l_act.add(self.id)
        l_rem.remove(self.id)

        for sm_i in copy.deepcopy(l_rem):
            if self._is_last:
                break
            middle_msg = self._get_middle_msg(round, l_rem, l_act, s_current)
            is_success = await self._send_msg_to_sm(sm_i, middle_msg)
            if is_success:
                return
            l_rem.remove(sm_i)

        final_msg = self._get_final_msg(round, l_act, s_current)
        await self._send_msg_to_dc(final_msg)

    def _update_round(self) -> None:
        self._round += 1

    # Protocol Implementation

    def _is_last(self, l_rem: SortedSet, l_act: SortedSet):
        return len(l_rem) == 0 or len(l_rem) + len(l_act) < self.n_min
