from typing import Optional

from time import time as now

from phe import paillier

from data_concentrator import DataConcentrator as DC
from smart_meter import SmartMeter as SM

class TestEnvironment:

    def __init__(self, dc_address: str, sm_addresses: list[str],
                 round_duration: int, phase_1_duration: int,
                 phase_2_duration: int,
                 key_len: int = paillier.DEFAULT_KEYSIZE):

        # Addresses of environment devices
        self._dc_address = dc_address
        self._sm_addresses = sm_addresses

        # Timouts
        self._test_start = None
        self._round_duration = round_duration
        self._phase_1_duration = phase_1_duration
        self._phase_2_duration = phase_2_duration

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
    def test_start(self) -> Optional[float]:
        return self._test_start

    @property
    def round_duration(self) -> int:
        return self._round_duration

    @property
    def phase_1_duration(self) -> int:
        return self._phase_1_duration

    @property
    def phase_2_duration(self) -> int:
        return self._phase_2_duration

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
