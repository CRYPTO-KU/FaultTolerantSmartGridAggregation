import copy

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable
from util import time

from url import URL

import asyncio
from aiohttp import web

from phase import Phase
from sortedcontainers import SortedSet

class DataConcentrator(ABC):
    
    # Constructor

    def __init__(self, address: URL, sm_addresses: list, n_min: int,
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
        self._data = {}
        self._l_rem = SortedSet()
        self._l_act = SortedSet()
        self._s_initial = 0
        self._s_final = 0

        # Output
        self._aggregates = {}

    # Public Interface

    @property
    def address(self) -> URL:
        """Data concentrator address."""
        return self._address

    @property
    def sm_addresses(self) -> list:
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
    def current_data(self) -> dict:
        return copy.deepcopy(self._data)

    @property
    def current_l_rem(self) -> SortedSet:
        return copy.deepcopy(self._l_rem)

    @property
    def current_l_act(self) -> SortedSet:
        return copy.deepcopy(self._l_act)

    @property
    def current_s_initial(self) -> int:
        return self._s_initial

    @property
    def current_s_final(self) -> int:
        return self._s_final

    @property
    def aggregates(self) -> dict:
        """Dictionary of aggregates for successful rounds."""
        return copy.deepcopy(self._aggregates)

    # Private Interface

    ## State

    def _increment_round(self) -> None:
        self._round += 1

    def _increment_phase(self) -> None:
        next_phase = {
            Phase.IDLE: Phase.FIRST,
            Phase.FIRST: Phase.SECOND,
            Phase.SECOND: Phase.IDLE
        }
        self._phase = next_phase[self._phase]

    def _add_data(self, sm_i: int, d_i) -> None:
        self._data[sm_i] = d_i

    def _clear_data(self) -> None:
        self._data = {}

    def _add_rem(self, sm_i: int) -> None:
        self._l_rem.add(sm_i)

    def _clear_rem(self) -> None:
        self._l_rem = SortedSet()

    def _set_l_act(self, l_act: list[int]) -> None:
        self._l_act = SortedSet(l_act)

    def _clear_act(self) -> None:
        self._l_act = SortedSet()

    def _set_s_initial(self, s_initial: int) -> None:
        self._s_initial = s_initial

    def _set_s_final(self, s_final: int) -> None:
        self._s_final = s_final

    # Server

    # def get_phase_1_request_handler(self) -> Callable[[web.Request], Awaitable[web.Response]]:
    #     async def handler(request: web.Request) -> web.Response:
    #         # Insure the DC is in phase 1
    #         if not self._phase == 1:
    #             raise web.HTTPBadRequest
    #         # Insure the request has a readable body
    #         if not (request.body_exists and request.can_read_body):
    #             raise web.HTTPBadRequest
    #         # Extract request data
    #         body = await request.json()
    #         sm_i = body["smartMeter"]
    #         t = body["round"]
    #         d_i = body["data"]
    #         self.phase_1_data_handler(sm_i, t, d_i)
    #         return web.json_response({
    #             "msg": "OK"
    #         })
    #     return handler

    # def get_phase_2_handler(self) -> Callable[[web.Request], Awaitable[web.Response]]:
    #     async def handler(request: web.Request) -> web.Response:
    #         # Insure the DC is in phase 2
    #         if not self._phase == 2:
    #             raise web.HTTPBadRequest
    #         # Insure the request has a readable body
    #         if not (request.body_exists and request.can_read_body):
    #             raise web.HTTPBadRequest
    #         # Extract request data
    #         body = await request.json()
    #         l_act = body["activeatedSmartMeters"]
    #         t = body["round"]
    #         s_final = body["sFinal"]
    #         self.phase_2_data_handler(l_act, t, s_final)
    #         return web.json_response({
    #             "msg": "OK"
    #         })
    #     return handler

    ## General Algorithm

    def _phase_1_data_handler(self, sm_i: int, t: int, d_i: int) -> None:
        # validate call
        if t != self.current_round or self.current_phase != Phase.FIRST:
            return
        self._add_data(sm_i, d_i)
        self._add_rem(sm_i)
        if len(self.current_l_rem) == len(self.sm_addresses):
            self._finish_phase_1(t)

    def _phase_2_data_handler(self, l_act: list[int], t: int, s_final: int) -> None:
        # validate call
        if t != self.current_round or self.current_phase != Phase.SECOND:
            return
        self._set_l_act(l_act)
        self._set_s_final(s_final)
        self._calculate_aggregate()
        self._finish_phase_2(t)

    def _finish_phase_1(self, t: int) -> None:
        # validate call
        if t != self.current_round or self.current_phase != Phase.FIRST:
            return
        # terminate round if not enough smart meters can participate
        if len(self.current_l_rem) < self.n_min:
            return

        self._calculate_s_initial()
        self._activate_smart_meter(
            self.current_l_rem[0],
            self.current_s_initial,
            self.current_l_rem,
            self.current_l_act
        )
        self._increment_phase()

    def _finish_phase_2(self, t: int) -> None:
        # validate call
        if t != self.current_round or self.current_phase != Phase.SECOND:
            return

        self._clear_data()
        self._clear_rem()
        self._clear_act()
        self._set_s_initial(0)
        self._set_s_final(0)
        self._increment_phase()

    async def _run_timer(self):
        while True:
            next_round_start = self.epoch + (self.current_round + 1) * self.round_duration
            await asyncio.sleep(time.time_remaining_until(next_round_start))
            self._increment_round()
            self._increment_phase()
            phase_1_timeout = next_round_start + self.phase_1_duration
            await asyncio.sleep(time.time_remaining_until(phase_1_timeout))
            if self.current_phase == Phase.IDLE:
                continue
            if self.current_phase == Phase.FIRST:
                self._finish_phase_1(self.current_round)
            phase_2_timeout = phase_1_timeout + self.phase_2_duration
            await asyncio.sleep(time.time_remaining_until(phase_2_timeout))
            if self.current_phase == Phase.SECOND:
                self._finish_phase_2(self.current_round)

    # Abstract Methods

    @abstractmethod
    def _calculate_s_initial(self) -> None:
        pass

    @abstractmethod
    def _activate_smart_meter(self, sm_i: int, s: int, l_rem: SortedSet, l_act: SortedSet) -> None:
        pass

    @abstractmethod
    def _calculate_aggregate(self) -> None:
        pass

    @abstractmethod
    def _initialize_server(self) -> None:
        pass

    def run(self) -> None:
        self._initialize_server()
        self._run_timer()
        
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
