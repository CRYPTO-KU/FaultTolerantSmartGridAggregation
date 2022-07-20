from typing import Optional

from time import time as now

from phe import paillier

from data_concentrator import DataConcentrator as DC
from smart_meter import SmartMeter as SM

class TestEnvironment:

    def __init__(self, dc_address: str, sm_addresses: list[str], n_min: int,
                 round_seconds: float, phase_1_seconds: float,
                 phase_2_seconds: float, key_len: int = paillier.DEFAULT_KEYSIZE):

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
        self._key_len = key_len

        # Generate public group key and secret key
        pk, sk = paillier.generate_paillier_keypair(key_len)
        self._pk = pk
        self._sk = sk

        # Data Concentrator and Smart Meters will be created later
        self._dc = None
        self._sm = None

    @property
    def dc_address(self) -> str:
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
    def key_length(self) -> int:
        return self._key_len

    @property
    def public_key(self) -> paillier.PaillierPublicKey:
        return self._pk

    @property
    def secret_key(self) -> paillier.PaillierPrivateKey:
        return self._sk

    @property
    def dc(self) -> Optional[DC]:
        return self._dc

    @property
    def sm(self) -> Optional[list[SM]]:
        return self._sm

    # Run test environment
    def run(self) -> None:
        # Record test start time
        self._test_start = now()

        # Create DC
        self._dc = DC(
            self.dc_address,
            self.sm_addresses,
            self.n_min,
            self.test_start,
            self.round_duration,
            self.phase_1_duration,
            self.phase_2_duration,
            self.public_key,
            self.secret_key
        )

        # Create SMs
        self._sm = [
            SM(
                address,
                self.dc_address,
                self.sm_addresses,
                self.n_min,
                self.test_start,
                self.round_duration,
                self.public_key
            )
            for address in self.sm_addresses
        ]

        # Run DC and SMs
        self.dc.run()
        for sm in self.sm:
            sm.run()
