import json
import secrets
from abc import ABC, abstractmethod
from time import sleep
from time import time as now
from typing import Any, Dict, Tuple

from .metadata import (
    Metadata,
    SMMaskingMetadata,
    SMHomomorphicMetadata,
    is_valid_sm_masking_metadata,
    is_valid_sm_homomorphic_metadata,
)
from .report import SMReport
from .network import NetworkManager
from . import crypto, time

################################################################################
# Classes
# NOTE:
# Don't call constructor directly.
# Use the factory method to make instances.
################################################################################


# Generic SM
# Abstract Class - Use concrete implemententations
class SM(ABC):
    def __init__(self, id: int, meta: Metadata, net_mngr: NetworkManager):
        self.id = id
        self.meta = meta
        self.net_mngr = net_mngr
        self.reports = []
        self.killed = False

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

    # NOTE: Override this in production
    def get_raw_measurement(self, round: int):
        return 1

    def _listen(self):
        # Start listening to incoming requests
        self.req_q = self.net_mngr.listen(self.meta.sm_addresses[self.id])

    def _stop(self):
        # Stop listening to incoming requests
        self.net_mngr.stop()

    def _run_single_round(self, round: int):
        # Wait for the right time to start round
        round_start = self.meta.t_start + self.meta.t_round_len * round
        sleep(time.remaining_until(round_start))

        self.reports.append(SMReport(id = self.id, t_start=now()))

        passthru, data = self._prep_data(round)

        ok = self._run_phase_1(round, data)
        if not ok:
            self.reports[round].t_end = now()
            return

        self._run_phase_2(round, passthru)
        self.reports[round].t_end = now()
        return

    @abstractmethod
    def _prep_data(self, round: int) -> Tuple[Any, Any]:
        pass

    def _run_phase_1(self, round: int, data) -> bool:
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_1_end = round_start + self.meta.t_phase_1_len
        req = {"id": self.id, "round": round, "data": data}
        ok = self.net_mngr.send(self.meta.dc_address, req, phase_1_end)
        if ok:
            self.reports[round].net_snd_succ += 1
            self.reports[round].net_snd_succ_size += len(json.dumps(req))
        else:
            self.reports[round].net_snd_fail += 1
            self.reports[round].net_snd_fail_size += len(json.dumps(req))
        return ok

    def _run_phase_2(self, round: int, passthru):
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_2_end = round_start + self.meta.t_round_len

        while now() < phase_2_end and not self.killed:
            if self.req_q.empty():
                sleep(0.1)
                continue

            req = self.req_q.get()
            self.reports[round].net_rcv += 1
            self.reports[round].net_rcv_size += len(json.dumps(req))

            if self._is_phase_2_request_valid(round, req):
                self.reports[round].activated = True
                self._act_phase_2(round, req, passthru)
                break

    def _act_phase_2(self, round: int, req: Dict, passthru):
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_2_end = round_start + self.meta.t_round_len

        # Move ourself from remaining to acted
        l_rem = tuple([sm for sm in req["l_rem"] if sm != self.id])
        l_act = tuple(req["l_act"] + [self.id])

        s_new = self._aggregate_to_s(round, req, passthru)

        while not self._is_last(l_rem, l_act):
            # Don't exceed time limit
            if now() >= phase_2_end:
                return
            next_sm = l_rem[0]
            data = {"round": round, "s": s_new, "l_rem": l_rem, "l_act": l_act}
            if self.meta.sm_addresses[next_sm].valid:
                ok = self.net_mngr.send(
                    self.meta.sm_addresses[next_sm],
                    data,
                    phase_2_end,
                )
                # We activated the next SM
                if ok:
                    self.reports[round].net_snd_succ += 1
                    self.reports[round].net_snd_succ_size += len(json.dumps(data))
                    return
                self.reports[round].net_snd_fail += 1
                self.reports[round].net_snd_fail_size += len(json.dumps(data))
            # We couldn't activate next SM
            # Remove it from the remaining SMs before trying with another one
            l_rem = l_rem[1:]

        # Report to DC if we reached the minimum participating SMs
        if len(l_act) >= self.meta.n_min and self.meta.dc_address.valid:
            # Don't exceed time limit
            if now() >= phase_2_end:
                return
            data = {"round": round, "s": s_new, "l_rem": l_rem, "l_act": l_act}
            ok = self.net_mngr.send(self.meta.dc_address, data, phase_2_end)
            if ok:
                self.reports[round].net_snd_succ += 1
                self.reports[round].net_snd_succ_size += len(json.dumps(data))
            else:
                self.reports[round].net_snd_fail += 1
                self.reports[round].net_snd_fail_size += len(json.dumps(data))

    @abstractmethod
    def _aggregate_to_s(self, round: int, req: Dict, passthru):
        pass

    def _is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        # Make sure request contains all required keys
        if not all(key in req for key in ["round", "s", "l_rem", "l_act"]):
            return False

        # Round should be correct
        if req["round"] != round:
            return False

        if not isinstance(req["l_rem"], list):
            return False
        if not isinstance(req["l_act"], list):
            return False

        # If we have an intersection, data is invalid
        intersection = set(req["l_rem"]) & set(req["l_act"])
        if len(intersection) > 0:
            return False

        # We shouldn't be doing phase 2 if we didn't do phase 1
        if self.id not in req["l_rem"]:
            return False

        for i in req["l_rem"]:
            if i not in range(len(self.meta.sm_addresses)):
                return False

        for i in req["l_act"]:
            if i not in range(len(self.meta.sm_addresses)):
                return False
            # We shouldn't be doing phase 2 if we already did it
            if i == self.id:
                return False

        return True

    def _is_last(self, l_rem: Tuple[int, ...], l_act: Tuple[int, ...]) -> bool:
        return len(l_rem) == 0 or (len(l_rem) + len(l_act)) < self.meta.n_min


# Masking SM
# Concrete implemententation of SM
class MaskingSM(SM):
    def __init__(self, id: int, meta: SMMaskingMetadata, net_mngr: NetworkManager):
        if not is_valid_sm_masking_metadata(meta):
            raise ValueError("Invalid smart meter masking metadata.")
        super().__init__(id, meta, net_mngr)
        self.meta = meta

    def _prep_data(self, round: int) -> Tuple[Any, Any]:
        s = secrets.randbelow(self.meta.k)
        p = crypto.prf(self.meta.prf_key, round)
        masked = (self.get_raw_measurement(round) + s + p) % self.meta.k
        return s, masked

    def _aggregate_to_s(self, round: int, req: Dict, passthru):
        return (passthru + req["s"]) % self.meta.k


# Homomorphic Encryption SM
# Concrete implemententation of SM
class HomomorphicSM(SM):
    def __init__(self, id: int, meta: SMHomomorphicMetadata, net_mngr: NetworkManager):
        if not is_valid_sm_homomorphic_metadata(meta):
            raise ValueError("Invalid smart meter homomorphic metadata.")
        super().__init__(id, meta, net_mngr)
        self.meta = meta

    def _prep_data(self, round: int) -> Tuple[Any, Any]:
        return None, None

    def _aggregate_to_s(self, round: int, req: Dict, passthru):
        agg = crypto.deserialize_homomorphic_number(req["s"], self.meta.pk)
        new = self.meta.pk.encrypt(self.get_raw_measurement(round))
        return crypto.serialize_homomorphic_number(agg + new)


################################################################################
# Factory
################################################################################


# Construct the correct type of SM based on the given metadata
def make_sm(
    id: int, meta: SMMaskingMetadata | SMHomomorphicMetadata, net_mngr: NetworkManager
) -> SM:
    if isinstance(meta, SMMaskingMetadata):
        return MaskingSM(id, meta, net_mngr)
    return HomomorphicSM(id, meta, net_mngr)
