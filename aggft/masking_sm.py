from smart_meter import SM
import secrets
from typing import Any, Dict, List, Tuple

class MaskingSM(SM):
    def __init__(self, id: int, dc_address: str, sm_addresses: List[str],
                 n_min: int, epoch_seconds: float, round_seconds: float,
                 k: int):

        super().__init__(id, dc_address, sm_addresses, n_min, epoch_seconds, round_seconds)
        self._k = k

    @property
    def k(self) -> int:
        return self._k

    def _get_si(self, round: int) -> int:
        return secrets.randbelow(self.k)

    def _update_s(self, s: int, si: int) -> int:
        return (s + si) % self.k
