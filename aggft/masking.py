import secrets

from data_concentrator import DC
from sortedcontainers import SortedSet
from typing import Any, Dict, List, Tuple
from types.url import URL

class MaskingDC(DC):
    def __init__(self, address: URL, sm_addresses: List[str], n_min: int,
                 epoch_seconds: float, round_seconds: float,
                 phase_1_seconds: float, phase_2_seconds: float,
                 k: int):
        super().__init__(address, sm_addresses, n_min, epoch_seconds, round_seconds, phase_1_seconds, phase_2_seconds)
        self._k = k

    # Public Interface

    ## Getters

    @property
    def k(self) -> int:
        return self._k

    def _generate_s_initial(self) -> int:
        return secrets.randbelow(self.k)

    def _calculate_aggregate(self, data: Dict[int, Any], l_act: SortedSet, s_init: int, s_final: int) -> int:
        masked_measurements_sum = 0
        for sm_i in l_act:
            masked_measurements_sum += data[sm_i]
        return masked_measurements_sum - (s_final - s_init) % self.k
