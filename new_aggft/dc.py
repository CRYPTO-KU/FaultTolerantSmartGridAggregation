import json
import secrets

from time            import sleep
from time            import time as now

from .util           import log
from .util.network   import NetworkManager
from .util           import prf
from .util           import time

from typing          import Dict, Tuple

from .model.metadata import DCMaskingMetadata, is_valid_dc_masking_metadata
from .model.report   import DCReport

class DC():
    def __init__(self, meta: DCMaskingMetadata, net_mngr: NetworkManager):
        if not is_valid_dc_masking_metadata(meta):
            raise ValueError("Invalid data concentrator masking metadata.")
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

        self.reports.append(DCReport(t_start = now()))

        data, prfs, l_rem = self._run_phase_1(round)
        self.reports[round].phase_1_count = len(l_rem)
        if len(l_rem) < self.meta.n_min:
            log.warning(f"[round {round}] {len(l_rem)} out of {self.meta.n_min} required smart meters participated in phase 1. Aborting round...")
            self.reports[round].terminated = True
            self.reports[round].t_end = now()
            return

        log.info(f"[round {round}] [phase 1] {len(l_rem)} smart meters participated in phase 1.")
        log.info(f"[round {round}] [phase 1] Data: {data}")
        s_initial = secrets.randbelow(self.meta.k)
        log.info(f"[round {round}] Activating first smart meter...")
        activated = self._activate_first_sm(round, s_initial, l_rem)
        if not activated:
            log.warning(f"[round {round}] Could not activate first smart meter. Aborting round...")
            self.reports[round].terminated = True
            self.reports[round].t_end = now()
            return
        log.success(f"[round {round}] Activated first smart meter.")
        self._run_phase_2(round, data, s_initial, prfs)
        self.reports[round].terminated = True
        self.reports[round].t_end = now()

    def _run_phase_1(self, round: int) -> Tuple[Dict, Dict, Tuple[int, ...]]:
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_1_end = round_start + self.meta.t_phase_1_len

        data = {}
        prfs = {}
        l_rem = []
        while now() < phase_1_end:
            if self.req_q.empty():
                continue

            self.reports[round].net_rcv += 1
            req = self.req_q.get()

            if self._is_phase_1_request_valid(round, req):
                data[req["id"]] = req["data"]
                prfs[req["id"]] = prf.PRF(self.meta.prf_keys[req["id"]], round)
                l_rem.append(req["id"])

            if len(l_rem) == len(self.meta.sm_addresses):
                break

        return data, prfs, tuple(sorted(l_rem))

    def _is_phase_1_request_valid(self, round: int, req: Dict) -> bool:
        # Make sure request contains all required keys
        if not all(key in req for key in ["round", "id", "data"]):
            return False

        # Round should be correct
        if req["round"] != round: return False

        if req["id"] not in range(len(self.meta.sm_addresses)): return False
        if not isinstance(req["data"], int): return False

        return True

    def _activate_first_sm(self, round: int, s_initial: int, l_rem: Tuple[int, ...]) -> bool:
        data = { "round": round, "s": s_initial, "l_rem": l_rem, "l_act": [] }
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_2_end = round_start + self.meta.t_round_len
        for address in self.meta.sm_addresses:
            if not address.valid: continue
            self.reports[round].net_snd += 1
            ok = self.net_mngr.send(address, json.dumps(data), phase_2_end)
            if ok: return True
        return False

    def _run_phase_2(self, round: int, data: Dict, s_initial: int, prfs: Dict):
        round_start = self.meta.t_start + self.meta.t_round_len * round
        phase_2_end = round_start + self.meta.t_round_len

        while now() < phase_2_end:
            if self.req_q.empty():
                continue

            self.reports[round].net_rcv += 1
            req = self.req_q.get()

            if self._is_phase_2_request_valid(round, req):
                masked_sum = sum(map(lambda id: data[id], req["l_act"]))
                prfs_l_act = sum(map(lambda id: prfs[id], req["l_act"]))
                aggregate = (masked_sum - (req["s"] - s_initial) - prfs_l_act) % self.meta.k
                log.success(f"Round {round} aggregate: {aggregate}.")
                self.reports[round].success = True
                self.reports[round].phase_2_count = req["l_act"]

    def _is_phase_2_request_valid(self, round: int, req: Dict) -> bool:
        # Make sure request contains all required keys
        if not all(key in req for key in ["round", "s", "l_act"]):
            return False

        # Round should be correct
        if req["round"] != round: return False

        if not isinstance(req["l_act"], list): return False
        for i in req["l_act"]:
            if i not in range(len(self.meta.sm_addresses)): return False

        return True
