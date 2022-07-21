import asyncio
import copy

from sortedcontainers import SortedSet
from util import time
from util.timeoutable_coroutine import TimeoutableCoroutine

# Types
from abc import ABC, abstractmethod
from types.phase import Phase
from types.url import URL
from typing import Any, Dict, List, Tuple

class DataConcentrator(ABC):
    
    # Constructor

    def __init__(self, address: URL, sm_addresses: List[str], n_min: int,
                 epoch_seconds: float, round_seconds: float,
                 phase_1_seconds: float, phase_2_seconds: float):

        # Addresses of environment devices
        self._address = address
        self._sm_addresses = sm_addresses
        self._n_min = n_min

        # Timouts
        self._t_epoch = epoch_seconds
        self._t_round = round_seconds
        self._t_phase_1 = phase_1_seconds
        self._t_phase_2 = phase_2_seconds

        # State
        self._round = -1
        self._phase = Phase.IDLE

        # Output
        self._aggregates = {}

    # Public Interface

    ## Entry Point

    async def run(self) -> None:
        while True:
            next_round_start = self.epoch + (self.current_round + 1) * self.round_duration
            await asyncio.sleep(time.remaining_until(next_round_start))
            self._update_round()
            aggregate = await self._run_round(self.current_round)
            if aggregate is not None:
                self._update_aggregates(self.current_round, aggregate)

    ## Getters

    @property
    def address(self) -> URL:
        """Data concentrator address."""
        return self._address

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
    def phase_1_duration(self) -> float:
        """Duration of the initial message sending phase in seconds."""
        return self._t_phase_1

    @property
    def phase_2_duration(self) -> float:
        """Duration of the final message sending phase in seconds."""
        return self._t_phase_2

    @property
    def current_round(self) -> int:
        """Index of the current round (zero-based)."""
        return self._round

    @property
    def current_phase(self) -> Phase:
        return self._phase

    @property
    def aggregates(self) -> Dict[int, int]:
        """Dictionary of aggregates for successful rounds."""
        return copy.deepcopy(self._aggregates)

    # Private Interface

    ## Algorithm

    async def _run_round(self, round: int):
        # Phase.IDLE -> Phase.FIRST
        self._update_phase()
        l_rem, data = await self._get_phase_1_server().run(
            timeout = self.phase_1_duration,
            round = round
        )
        s_init = self._generate_s_initial()
        # terminate round if not enough smart meters can participate
        if len(l_rem) < self.n_min:
            return

        self._activate_smart_meter(l_rem, s_init)
        # Phase.FIRST -> Phase.SECOND
        self._update_phase()
        l_act, s_final = await self._get_phase_2_server().run(
            timeout = self.phase_2_duration,
            round = round
        )
        # Phase.SECOND -> Phase.IDLE
        self._update_phase()
        return self._calculate_aggregate(data, l_act, s_init, s_final)

    ## Setters

    def _update_round(self) -> None:
        self._round += 1

    def _update_phase(self) -> None:
        next_phase = {
            Phase.IDLE: Phase.FIRST,
            Phase.FIRST: Phase.SECOND,
            Phase.SECOND: Phase.IDLE
        }
        self._phase = next_phase[self._phase]

    def _update_aggregates(self, round: int, aggregate: int) -> None:
        self._aggregates[round] = aggregate

    ## Server

    @abstractmethod
    def _get_phase_1_server(self) -> TimeoutableCoroutine[Tuple[SortedSet, Dict[int, Any]]]:
        pass

    @abstractmethod
    def _get_phase_2_server(self) -> TimeoutableCoroutine[Tuple[SortedSet, int]]:
        pass

    ## Others

    @abstractmethod
    def _generate_s_initial(self) -> int:
        pass

    @abstractmethod
    def _activate_smart_meter(self, l_rem: SortedSet, s_init: int) -> None:
        pass

    @abstractmethod
    def _calculate_aggregate(self, data: Dict[int, Any], l_act: SortedSet, s_init: int, s_final: int) -> int:
        pass
