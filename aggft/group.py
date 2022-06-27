from phe import paillier

from data_concentrator import DC
from smart_meter import SM

class Group:

    def __init__(self, sm_count : int, key_len: int = paillier.DEFAULT_KEYSIZE):
        pk, sk = paillier.generate_paillier_keypair(key_len)

        self._dc = DC()
        self._sm = [SM() for _ in range(sm_count)]
        self._kl = key_len
        self._pk = pk
        self._sk = sk

    @property
    def data_concentrator(self) -> DC:
        return self._dc

    @property
    def smart_meters(self) -> list[SM]:
        return list(self._sm)

    @property
    def sart_meters_count(self) -> int:
        return len(self._sm)
