# Standard Library Imports

import json
import secrets

from time import sleep
from time import time as now

# Project Imports

from ..util import log
from ..util import network
from ..util import prf
from ..util import time

# Standard Library Type Imports

from typing import Dict, Tuple

# Project Type Imports

from ..model.round import RoundMetadata

def run_forever(port: network.Port, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, k: int, prf_key: bytes):
    # Wait for the right time to start operation
    log.info("Waiting for operation start...")
    sleep(time.remaining_until(meta.start))
    log.info("Operation started.")
    log.info(f"Round {0} started.")
    run_single_round(0, port, sm_addresses, meta, k, prf_key)
    log.info(f"Round {0} ended.")

def run_single_round(round: int, port: network.Port, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, k: int, prf_key: bytes):
    # Wait for the right time to start round
    round_start = meta.start + meta.round_len * round
    sleep(time.remaining_until(round_start))
    data, prfs, l_rem = run_phase_1(round, port, sm_addresses, meta, prf_key)
    if len(l_rem) < meta.n_min:
        log.warning(f"[round {round}] {len(l_rem)} out of {meta.n_min} required smart meters participated in phase 1. Aborting round...")
        return
    log.info(f"[round {round}] [phase 1] {len(l_rem)} smart meters participated in phase 1.")
    log.info(f"[round {round}] [phase 1] Data: {data}")
    s_initial = secrets.randbelow(k)
    log.info(f"[round {round}] Activating first smart meter...")
    activated = activate_first_sm(round, sm_addresses, meta, s_initial, l_rem)
    if not activated:
        log.warning(f"[round {round}] Could not activate first smart meter. Aborting round...")
        pass
    log.success(f"[round {round}] Activated first smart meter.")
    run_phase_2(round, port, sm_addresses, meta, k, data, s_initial, prfs)

def run_phase_1(round: int, port: network.Port, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, prf_key: bytes) -> Tuple[Dict, Dict, Tuple[int, ...]]:
    round_start = meta.start + meta.round_len * round
    phase_1_end = round_start + meta.phase_1_len
    requests = network.listen_multiple(port, phase_1_end, "<START>", "<END>", phase_1_early_stopper(round, sm_addresses))
    validator = phase_1_request_validator(round, sm_addresses)
    valid_requests = map(json.loads, filter(validator, requests))
    data = {}
    prfs = {}
    l_rem = []
    for r in valid_requests:
        data[r["id"]] = r["data"]
        prfs[r["id"]] = prf.PRF(prf_key, round)
        l_rem.append(r["id"])
    return data, prfs, tuple(sorted(l_rem))

def run_phase_2(round: int, port: network.Port, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, k: int, data: Dict, s_initial: int, prfs: Dict):
    round_start = meta.start + meta.round_len * round
    phase_2_end = round_start + meta.round_len
    requests = network.listen_multiple(port, phase_2_end, "<START>", "<END>", phase_2_early_stopper(round, sm_addresses))
    validator = phase_2_request_validator(round, sm_addresses)
    valid_requests = list(map(json.loads, filter(validator, requests)))
    if len(valid_requests) == 0: return
    final_data = valid_requests[0]
    
    masked_sum = sum(map(lambda id: data[id], final_data["l_act"]))
    prfs_l_act = sum(map(lambda id: prfs[id], final_data["l_act"]))
    aggregate = (masked_sum - (final_data["s"] - s_initial) - prfs_l_act) % k
    log.success(f"Round {round} aggregate: {aggregate}.")

def activate_first_sm(round: int, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, s_initial: int, l_rem: Tuple[int, ...]) -> bool:
    data = { "round": round, "s": s_initial, "l_rem": l_rem, "l_act": [] }
    round_start = meta.start + meta.round_len * round
    phase_2_end = round_start + meta.round_len
    for address in sm_addresses:
        is_ok = network.send(address, json.dumps(data), phase_2_end, "<START>", "<END>")
        if is_ok:
            return True
    return False

def phase_1_early_stopper(round: int, sm_addresses: Tuple[network.Address, ...]):
    validator = phase_1_request_validator(round, sm_addresses)
    def early_stopper(data: Tuple[str, ...]):
        valid_count = 0
        for d in data:
            if validator(d): valid_count += 1
        if valid_count == len(sm_addresses): return True
        return False
    return early_stopper

def phase_1_request_validator(round: int, sm_addresses: Tuple[network.Address, ...]):
    def validator(data: str) -> bool:
        dict_includes_keys = lambda dict, keys: dict.keys() >= keys
        try:
            json_data = json.loads(data)
            if not dict_includes_keys(json_data, {"round", "id", "data"}): return False
            if json_data["round"] != round: return False
            if json_data["id"] not in range(len(sm_addresses)): return False
            if not isinstance(json_data["data"], int): return False
            return True
        except json.JSONDecodeError:
            return False
    return validator

def phase_2_early_stopper(round: int, sm_addresses: Tuple[network.Address, ...]):
    validator = phase_2_request_validator(round, sm_addresses)
    def early_stopper(data: Tuple[str, ...]):
        for d in data:
            if validator(d): return True
        return False
    return early_stopper

def phase_2_request_validator(round: int, sm_addresses: Tuple[network.Address, ...]):
    def validator(data: str) -> bool:
        dict_includes_keys = lambda dict, keys: dict.keys() >= keys
        try:
            json_data = json.loads(data)
            if not dict_includes_keys(json_data, {"round", "s", "l_act"}): return False
            if json_data["round"] != round: return False
            if not isinstance(json_data["l_act"], list): return False
            for i in json_data["l_act"]:
                if i not in range(len(sm_addresses)): return False
            return True
        except json.JSONDecodeError:
            return False
    return validator
