from typing import Optional

from time import time as now


from phe import paillier

import asyncio

from aggft.http_masking import HTTPMaskingDC
from aggft.http_masking_sm import TestHTTPMaskingSM

from aggft.types.url import URL

class TestEnvironment:

    def __init__(self, dc_address: URL, sm_addresses: list[str], n_min: int,
                 round_seconds: float, phase_1_seconds: float,
                 phase_2_seconds: float, k: int):

        # Addresses of environment devices
        self._dc_address = dc_address
        self._sm_addresses = sm_addresses
        self._n_min = n_min

        # Timouts
        self._t_epoch = None
        self._t_round = round_seconds
        self._t_phase_1 = phase_1_seconds
        self._t_phase_2 = phase_2_seconds

        # Cryptographic keys length
        self._k = k

        # Data Concentrator and Smart Meters will be created later
        self._dc = None
        self._sm = None

    @property
    def dc_address(self) -> URL:
        return self._dc_address

    @property
    def sm_addresses(self) -> list[str]:
        return list(self._sm_addresses)

    @property
    def n_min(self) -> int:
        return self._n_min

    @property
    def epoch(self) -> Optional[float]:
        return self._t_epoch

    @property
    def round_duration(self) -> float:
        return self._t_round

    @property
    def phase_1_duration(self) -> float:
        return self._t_phase_1

    @property
    def phase_2_duration(self) -> float:
        return self._t_phase_2

    @property
    def dc(self) -> Optional[HTTPMaskingDC]:
        return self._dc

    @property
    def sm(self) -> Optional[list[TestHTTPMaskingSM]]:
        return self._sm

    # Run test environment
    async def run(self) -> None:
        # Record test start time
        self._test_start = now()

        # Create DC
        self._dc = HTTPMaskingDC(
            self.dc_address,
            self.sm_addresses,
            self.n_min,
            self._test_start,
            self.round_duration,
            self.phase_1_duration,
            self.phase_2_duration,
            self._k
        )

        # Create SMs
        self._sm = [
            TestHTTPMaskingSM(
                i,
                self.dc_address.to_str,
                self.sm_addresses,
                self.n_min,
                self._test_start,
                self.round_duration,
                self._k
            )
            for i, address in enumerate(self.sm_addresses)
        ]

        # Run DC and SMs
        await asyncio.gather(
            self._dc.run(), *[sm.run() for sm in self._sm]
        )
