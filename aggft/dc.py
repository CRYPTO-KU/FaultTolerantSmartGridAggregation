import json
import secrets
from abc import ABC, abstractmethod
from time import sleep
from time import time as now
from typing import Dict, Tuple

from model.metadata import (
    DCMaskingMetadata,
    DCPaillierMetadata,
    Metadata,
    is_valid_dc_masking_metadata,
    is_valid_dc_paillier_metadata,
)
from model.report import DCReport
from util import log, paillier, prf, time
from util.network import NetworkManager

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
        log.info("Waiting for operation start...")
        sleep(time.remaining_until(self.meta.t_start))
        log.info("Operation started.")

        round = 0
        while True:
            log.info(f"Round {round} started.")
            self._run_single_round(round)
            log.info(f"Round {round} ended.")
            round += 1

    def run_once(self):
        self._listen()

        # Wait for the right time to start operation
        log.info("Waiting for operation start...")
        sleep(time.remaining_until(self.meta.t_start))
        log.info("Operation started.")

        log.info(f"Round started.")
        self._run_single_round(0)
        log.info(f"Round ended.")

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
        self.reports[round].t_phase_1 = now()
        if len(l_rem) < self.meta.n_min:
            log.warning(
                f"[round {round}] {len(l_rem)} out of {self.meta.n_min} required smart meters participated in phase 1. Aborting round..."
            )
            self.reports[round].terminated = True
            self.reports[round].t_end = now()
            return

        log.info(
            f"[round {round}] [phase 1] {len(l_rem)} smart meters participated in phase 1."
        )
        log.info(f"[round {round}] [phase 1] Data: {data}")
        s_initial = self._generate_s_initial()
        log.info(f"[round {round}] Activating first smart meter...")
        activated = self._activate_first_sm(round, s_initial, l_rem)
        if not activated:
            log.warning(
                f"[round {round}] Could not activate first smart meter. Aborting round..."
            )
            self.reports[round].terminated = True
            self.reports[round].t_end = now()
            return
        log.success(f"[round {round}] Activated first smart meter.")
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

            if self._is_phase_1_request_valid(round, req):
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
            self.reports[round].net_snd += 1
            self.reports[round].net_snd_size += len(json.dumps(data))
            ok = self.net_mngr.send(address, data, phase_2_end)
            if ok:
                return True
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
                log.success(f"Round {round} aggregate: {aggregate}.")
                self.reports[round].success = True
                self.reports[round].phase_2_count = len(req["l_act"])
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
        return isinstance(req["data"], int)

    def _parse_phase_1_request(self, round: int, req: Dict) -> Dict:
        return {
            "masked": req["data"],
            "prf": prf.PRF(self.meta.prf_keys[req["id"]], round),
        }

    def _generate_s_initial(self):
        return secrets.randbelow(self.meta.k)

    def _specific_is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        return True

    def _calc_aggregate(self, round: int, data: Dict, s_initial, req: Dict):
        masked_sum = sum(map(lambda id: data[id]["masked"], req["l_act"]))
        prfs_l_act = sum(map(lambda id: data[id]["prf"], req["l_act"]))
        return (masked_sum - (req["s"] - s_initial) - prfs_l_act) % self.meta.k


# Paillier Homomorphic Encryption DC
# Concrete implemententation of DC
class PaillierDC(DC):
    def __init__(self, meta: DCPaillierMetadata, net_mngr: NetworkManager):
        if not is_valid_dc_paillier_metadata(meta):
            raise ValueError("Invalid data concentrator Paillier metadata.")
        super().__init__(meta, net_mngr)
        self.meta = meta

    def _specific_is_phase_1_request_valid(self, round: int, req: Dict) -> bool:
        return True

    def _parse_phase_1_request(self, round: int, req: Dict) -> Dict:
        return {}

    def _generate_s_initial(self):
        m = self.meta.pk.encrypt(0)
        return paillier.serialize_encrypted_number(m)

    def _specific_is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        return True

    def _calc_aggregate(self, round: int, data: Dict, s_initial, req: Dict):
        m = req["s"]
        s = paillier.deserialize_encrypted_number(m, self.meta.pk)
        return self.meta.sk.decrypt(s)


################################################################################
# Factory
################################################################################

# Construct the correct type of DC based on the given metadata
def make_dc(
    meta: DCMaskingMetadata | DCPaillierMetadata, net_mngr: NetworkManager
) -> DC:
    if isinstance(meta, DCMaskingMetadata):
        return MaskingDC(meta, net_mngr)
    return PaillierDC(meta, net_mngr)
