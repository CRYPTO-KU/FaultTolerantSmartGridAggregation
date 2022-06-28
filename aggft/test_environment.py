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
        self._round_duration = round_duration
        self._phase_1_duration = phase_1_duration
        self._phase_2_duration = phase_2_duration

        # Cryptographic keys length
        self._key_len = key_len

        # Generate public group key and secret key
        pk, sk = paillier.generate_paillier_keypair(key_len)
        self._pk = pk
        self._sk = sk

    @property
    def dc_address(self) -> str:
        return self._dc_address

    @property
    def sm_addresses(self) -> list[str]:
        return list(self._sm_addresses)

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
