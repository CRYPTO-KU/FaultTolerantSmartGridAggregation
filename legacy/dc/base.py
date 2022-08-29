import asyncio
import copy

from sortedcontainers import SortedSet
from aggft.util import time
from aggft.util.timeoutable_coroutine import TimeoutableCoroutine

# Types
from abc import ABC, abstractmethod
from aggft.types.phase import Phase
from typing import Any, Dict, List, Tuple

class BaseDC(ABC):
    async def run(self) -> None:
        while True:
            next_round_start = self.epoch + (self.current_round + 1) * self.round_duration
            await asyncio.sleep(time.remaining_until(next_round_start))
            self._update_round()
            aggregate = await self._run_round(self.current_round)
            if aggregate is not None:
                self._update_aggregates(self.current_round, aggregate)

    async def _run_round(self, round: int):
        # Phase.IDLE -> Phase.FIRST
        self._update_phase()
        l_rem, data = await self._get_phase_1_server().run(
            timeout = self.phase_1_duration,
            round = round,
            n_min = self.n_min,
            port = self.port
        )
        print(l_rem, data)
        s_init = self._generate_s_initial()
        # terminate round if not enough smart meters can participate
        if len(l_rem) < self.n_min:
            return

        await self._activate_smart_meter(l_rem, s_init)
        # Phase.FIRST -> Phase.SECOND
        self._update_phase()
        l_act, s_final = await self._get_phase_2_server().run(
            timeout = self.phase_2_duration,
            round = round,
            port = self.port
        )
        # Phase.SECOND -> Phase.IDLE
        self._update_phase()
        if len(l_act) > 0:
            return self._calculate_aggregate(data, l_act, s_init, s_final)

    @abstractmethod
    def _get_phase_1_server(self) -> TimeoutableCoroutine[Tuple[SortedSet, Dict[int, Any]]]:
        pass

    @abstractmethod
    def _get_phase_2_server(self) -> TimeoutableCoroutine[Tuple[SortedSet, int]]:
        pass

    ## Others

    @abstractmethod
    async def _activate_smart_meter(self, l_rem: SortedSet, s_init: int) -> None:
        pass

    @abstractmethod
    def _generate_s_initial(self) -> int:
        pass

    @abstractmethod
    def _calculate_aggregate(self, data: Dict[int, Any], l_act: SortedSet, s_init: int, s_final: int) -> int:
        pass
