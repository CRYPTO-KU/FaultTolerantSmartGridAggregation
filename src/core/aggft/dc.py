import json
import secrets
from abc import ABC, abstractmethod
from time import sleep
from time import time as now
from typing import Dict, Tuple

from .metadata import (
    DCMaskingMetadata,
    DCHomomorphicMetadata,
    Metadata,
    is_valid_dc_masking_metadata,
    is_valid_dc_homomorphic_metadata,
)
from .report import DCReport
from .network import NetworkManager
from . import crypto, time

################################################################################
# Classes
# NOTE:
# Don't call constructor directly.
# Use the factory method to make instances.
################################################################################


# Generic DC
# Abstract Class - Use concrete implemententations
class DC(ABC):
    def __init__(self, meta: Metadata, net_mngr: NetworkManager):
        self.meta = meta
        self.net_mngr = net_mngr
        self.reports = []

    def run_forever(self):
        self._listen()

        # Wait for the right time to start operation
        sleep(time.remaining_until(self.meta.t_start))

        round = 0
        while True:
            self._run_single_round(round)
            round += 1

    def run_once(self):
        self._listen()

        # Wait for the right time to start operation
        sleep(time.remaining_until(self.meta.t_start))

        self._run_single_round(0)

        self._stop()

    def _listen(self):
        # Start listening to incoming requests
        self.req_q = self.net_mngr.listen(self.meta.dc_address)

    def _stop(self):
        # Stop listening to incoming requests
        self.net_mngr.stop()

    def _run_single_round(self, round: int):
        # Wait for the right time to start round
        round_start = self.meta.t_start + self.meta.t_round_len * round
        sleep(time.remaining_until(round_start))

        self.reports.append(DCReport(t_start=now()))

        data, l_rem = self._run_phase_1(round)
        self.reports[round].phase_1_count = len(l_rem)
        self.reports[round].phase_1_sms = l_rem
        self.reports[round].t_phase_1 = now()
        if len(l_rem) < self.meta.n_min:
            self.reports[round].terminated = True
            self.reports[round].t_end = now()
            return

        s_initial = self._generate_s_initial()
        activated = self._activate_first_sm(round, s_initial, l_rem)
        if not activated:
            self.reports[round].terminated = True
            self.reports[round].t_end = now()
            return
        self._run_phase_2(round, data, s_initial)
        self.reports[round].terminated = True
        self.reports[round].t_end = now()

    def _run_phase_1(self, round: int) -> Tuple[Dict, Tuple[int, ...]]:
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_1_end = round_start + self.meta.t_phase_1_len

        data = {}
        l_rem = []
        while now() < phase_1_end:
            if self.req_q.empty():
                sleep(0.1)
                continue

            req = self.req_q.get()
            self.reports[round].net_rcv += 1
            self.reports[round].net_rcv_size += len(json.dumps(req))

            if self._is_phase_1_request_valid(round, req) and req["id"] not in l_rem:
                data[req["id"]] = self._parse_phase_1_request(round, req)
                l_rem.append(req["id"])

            if len(l_rem) == len(self.meta.sm_addresses):
                break

        return data, tuple(sorted(l_rem))

    def _is_phase_1_request_valid(self, round: int, req: Dict) -> bool:
        generic_valid = self._generic_is_phase_1_request_valid(round, req)
        specific_valid = self._specific_is_phase_1_request_valid(round, req)
        return generic_valid and specific_valid

    def _generic_is_phase_1_request_valid(self, round: int, req: Dict) -> bool:
        # Make sure request contains all required keys
        if not all(key in req for key in ["round", "id", "data"]):
            return False

        # Round should be correct
        if req["round"] != round:
            return False

        if req["id"] not in range(len(self.meta.sm_addresses)):
            return False

        return True

    @abstractmethod
    def _specific_is_phase_1_request_valid(self, round: int, req: Dict) -> bool:
        pass

    @abstractmethod
    def _parse_phase_1_request(self, round: int, req: Dict) -> Dict:
        pass

    @abstractmethod
    def _generate_s_initial(self):
        pass

    def _activate_first_sm(self, round: int, s_initial, l_rem: Tuple[int, ...]) -> bool:
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_2_end = round_start + self.meta.t_round_len
        while len(l_rem) > 0:
            data = {"round": round, "s": s_initial, "l_rem": l_rem, "l_act": []}
            sm_id = l_rem[0]
            address = self.meta.sm_addresses[sm_id]
            if not address.valid:
                l_rem = l_rem[1:]
                continue
            ok = self.net_mngr.send(address, data, phase_2_end)
            if ok:
                self.reports[round].net_snd_succ += 1
                self.reports[round].net_snd_succ_size += len(json.dumps(data))
                return True
            self.reports[round].net_snd_fail += 1
            self.reports[round].net_snd_fail_size += len(json.dumps(data))
            l_rem = l_rem[1:]
        return False

    def _run_phase_2(self, round: int, data: Dict, s_initial):
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_2_end = round_start + self.meta.t_round_len

        while now() < phase_2_end:
            if self.req_q.empty():
                sleep(0.1)
                continue

            req = self.req_q.get()
            self.reports[round].net_rcv += 1
            self.reports[round].net_rcv_size += len(json.dumps(req))

            if self._is_phase_2_request_valid(round, req):
                aggregate = self._calc_aggregate(round, data, s_initial, req)
                self.reports[round].success = True
                self.reports[round].phase_2_count = len(req["l_act"])
                self.reports[round].phase_2_sms = req["l_act"]
                break

    def _is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        generic_valid = self._generic_is_phase_2_request_valid(round, req)
        specific_valid = self._specific_is_phase_2_request_valid(round, req)
        return generic_valid and specific_valid

    def _generic_is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        # Make sure request contains all required keys
        if not all(key in req for key in ["round", "s", "l_act"]):
            return False

        # Round should be correct
        if req["round"] != round:
            return False

        if not isinstance(req["l_act"], list):
            return False
        for i in req["l_act"]:
            if i not in range(len(self.meta.sm_addresses)):
                return False

        return True

    @abstractmethod
    def _specific_is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        pass

    @abstractmethod
    def _calc_aggregate(self, round: int, data: Dict, s_initial, req: Dict):
        pass


# Masking DC
# Concrete implemententation of DC
class MaskingDC(DC):
    def __init__(self, meta: DCMaskingMetadata, net_mngr: NetworkManager):
        if not is_valid_dc_masking_metadata(meta):
            raise ValueError("Invalid data concentrator masking metadata.")
        super().__init__(meta, net_mngr)
        self.meta = meta

    def _specific_is_phase_1_request_valid(self, round: int, req: Dict) -> bool:
        return "data" in req and isinstance(req["data"], int)

    def _parse_phase_1_request(self, round: int, req: Dict) -> Dict:
        return {
            "masked": req["data"],
            "prf": crypto.prf(self.meta.prf_keys[req["id"]], round),
        }

    def _generate_s_initial(self):
        return secrets.randbelow(self.meta.k)

    def _specific_is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        return True

    def _calc_aggregate(self, round: int, data: Dict, s_initial, req: Dict):
        masked_sum = sum(map(lambda id: data[id]["masked"], req["l_act"]))
        prfs_l_act = sum(map(lambda id: data[id]["prf"], req["l_act"]))
        return (masked_sum - (req["s"] - s_initial) - prfs_l_act) % self.meta.k


# Homomorphic Encryption DC
# Concrete implemententation of DC
class HomomorphicDC(DC):
    def __init__(self, meta: DCHomomorphicMetadata, net_mngr: NetworkManager):
        if not is_valid_dc_homomorphic_metadata(meta):
            raise ValueError("Invalid data concentrator homomorphic metadata.")
        super().__init__(meta, net_mngr)
        self.meta = meta

    def _specific_is_phase_1_request_valid(self, round: int, req: Dict) -> bool:
        return True

    def _parse_phase_1_request(self, round: int, req: Dict) -> Dict:
        return {}

    def _generate_s_initial(self):
        m = self.meta.pk.encrypt(0)
        return crypto.serialize_homomorphic_number(m)

    def _specific_is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        return True

    def _calc_aggregate(self, round: int, data: Dict, s_initial, req: Dict):
        m = req["s"]
        s = crypto.deserialize_homomorphic_number(m, self.meta.pk)
        return self.meta.sk.decrypt(s)


################################################################################
# Factory
################################################################################


# Construct the correct type of DC based on the given metadata
def make_dc(
    meta: DCMaskingMetadata | DCHomomorphicMetadata, net_mngr: NetworkManager
) -> DC:
    if isinstance(meta, DCMaskingMetadata):
        return MaskingDC(meta, net_mngr)
    return HomomorphicDC(meta, net_mngr)
