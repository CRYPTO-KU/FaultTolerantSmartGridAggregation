import secrets

from abc            import ABC, abstractmethod

from time           import sleep
from time           import time as now

from util.network   import NetworkManager
from util           import log
from util           import prf
from util           import time
from util           import paillier

from typing         import Any, Dict, Tuple

from model.metadata import Metadata
from model.metadata import SMMaskingMetadata, is_valid_sm_masking_metadata
from model.metadata import SMPaillierMetadata, is_valid_sm_paillier_metadata
from model.report   import SMReport


################################################################################
# Classes
# NOTE: Use the factory method to make instances.
################################################################################


# Generic SM
# Abstract Class - Use concrete implemententations
class SM(ABC):
    def __init__(self, id: int, meta: Metadata, net_mngr: NetworkManager):
        self.id       = id
        self.meta     = meta
        self.net_mngr = net_mngr
        self.reports  = []

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

        self.reports.append(SMReport(t_start = now()))

        passthru, data = self._prep_data(round)

        ok = self._run_phase_1(round, data)
        if not ok:
            log.warning(f"[round {round}] [phase 1] Could not send data to data concentrator. Aborting round...")
            self.reports[round].t_end = now()
            return

        log.success(f"[round {round}] [phase 1] Sent data to data concentrator.")
        self._run_phase_2(round, passthru)
        log.info(f"[round {round}] [phase 2] Phase done.")
        log.info(f"[round {round}] Ending round...")
        self.reports[round].t_end = now()
        return

    @abstractmethod
    def _prep_data(self, round: int) -> Tuple[Any, Any]:
        pass
    
    def _run_phase_1(self, round: int, data) -> bool:
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_1_end = round_start + self.meta.t_phase_1_len
        self.reports[round].net_snd += 1
        req = { "id": self.id, "round": round, "data": data }
        return self.net_mngr.send(self.meta.dc_address, req, phase_1_end)

    def _run_phase_2(self, round: int, passthru):
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_2_end = round_start + self.meta.t_round_len

        while now() < phase_2_end:
            if self.req_q.empty():
                sleep(0.1)
                continue

            self.reports[round].net_rcv += 1
            req = self.req_q.get()

            if self._is_phase_2_request_valid(round, req):
                self._act_phase_2(round, req, passthru)
                break

    def _act_phase_2(self, round: int, req: Dict, passthru):
        log.info(f"[round {round}] [phase 2] Got activated.")

        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_2_end = round_start + self.meta.t_round_len

        # Move ourself from remaining to acted
        l_rem = tuple([sm for sm in req["l_rem"] if sm != self.id])
        l_act = tuple(req["l_act"] + [self.id])

        s_new = self._aggregate_to_s(round, req, passthru)

        while not self._is_last(l_rem, l_act):
            # Don't exceed time limit
            if now() >= phase_2_end: return
            next_sm = l_rem[0]
            data = { "round": round, "s": s_new, "l_rem": l_rem, "l_act": l_act }
            if self.meta.sm_addresses[next_sm].valid:
                self.reports[round].net_snd += 1
                ok = self.net_mngr.send(
                    self.meta.sm_addresses[next_sm],
                    data,
                    phase_2_end,
                )
                # We activated the next SM
                if ok: return
            # We couldn't activate next SM
            # Remove it from the remaining SMs before trying with another one
            l_rem = tuple([sm for sm in l_rem if sm != next_sm])

        # Report to DC if we reached the minimum participating SMs
        if len(l_rem) + len(l_act) >= self.meta.n_min and self.meta.dc_address.valid:
            # Don't exceed time limit
            if now() >= phase_2_end: return
            data = { "round": round, "s": s_new, "l_rem": l_rem, "l_act": l_act }
            self.reports[round].net_snd += 1
            self.net_mngr.send(
                self.meta.dc_address,
                data,
                phase_2_end
            )

    @abstractmethod
    def _aggregate_to_s(self, round: int, req: Dict, passthru):
        pass

    def _is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        # Make sure request contains all required keys
        if not all(key in req for key in ["round", "s", "l_rem", "l_act"]):
            return False

        # Round should be correct
        if req["round"] != round: return False

        if not isinstance(req["l_rem"], list): return False
        if not isinstance(req["l_act"], list): return False

        # If we have an intersection, data is invalid
        intersection = set(req["l_rem"]) & set(req["l_act"])
        if len(intersection) > 0: return False

        for i in req["l_rem"]:
            if i not in range(len(self.meta.sm_addresses)): return False

        for i in req["l_act"]:
            if i not in range(len(self.meta.sm_addresses)): return False
            # We shouldn't be doing phase 2 if we already did it
            if i == self.id: return False

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
        p = prf.PRF(self.meta.prf_key, round)
        masked = (self.get_raw_measurement(round) + s + p) % self.meta.k
        return s, masked

    def _aggregate_to_s(self, round: int, req: Dict, passthru):
        return (passthru + req["s"]) % self.meta.k


# Paillier Homomorphic Encryption SM
# Concrete implemententation of SM
class PaillierSM(SM):
    def __init__(self, id: int, meta: SMPaillierMetadata, net_mngr: NetworkManager):
        if not is_valid_sm_paillier_metadata(meta):
            raise ValueError("Invalid smart meter Paillier metadata.")
        super().__init__(id, meta, net_mngr)
        self.meta = meta

    def _prep_data(self, round: int) -> Tuple[Any, Any]:
        return None, None

    def _aggregate_to_s(self, round: int, req: Dict, passthru):
        agg = paillier.deserialize_encrypted_number(req["s"], self.meta.pk)
        new = self.meta.pk.encrypt(self.get_raw_measurement(round))
        return paillier.serialize_encrypted_number(agg + new)


################################################################################
# Factory
################################################################################


# Construct the correct type of SM based on the given metadata
def make_sm(id: int, meta: SMMaskingMetadata | SMPaillierMetadata, net_mngr: NetworkManager) -> SM:
    if isinstance(meta, SMMaskingMetadata):
        return MaskingSM(id, meta, net_mngr)
    return PaillierSM(id, meta, net_mngr)
