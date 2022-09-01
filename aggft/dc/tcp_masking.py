# Standard Library Imports

import json

from time import sleep
from time import time as now

# Project Imports

from ..util import log
from ..util import network
from ..util import time

# Standard Library Type Imports

from typing import Dict, Tuple

# Project Type Imports

from ..model.round import RoundMetadata

def run_forever(port: network.Port, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, k: int):
    # Wait for the right time to start operation
    log.info("Waiting for operation start...")
    sleep(time.remaining_until(meta.start))
    log.info("Operation started.")
    log.info(f"Round {0} started.")
    run_single_round(0, port, sm_addresses, meta, k)
    log.info(f"Round {0} ended.")

def run_single_round(round: int, port: network.Port, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, k: int):
    # Wait for the right time to start round
    round_start = meta.start + meta.round_len * round
    sleep(time.remaining_until(round_start))
    data, l_rem = run_phase_1(round, port, sm_addresses, meta)
    if len(l_rem) < meta.n_min:
        log.info(f"[round {round}] {len(l_rem)} out of {meta.n_min} required smart meters participated in phase 1. Aborting round...")
        return
    print(data)
    print(l_rem)

def run_phase_1(round: int, port: network.Port, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata) -> Tuple[Dict, Tuple[int, ...]]:
    round_start = meta.start + meta.round_len * round
    phase_1_end = round_start + meta.phase_1_len
    requests = network.listen_multiple(port, phase_1_end, "<START>", "<END>", phase_1_early_stopper(round, sm_addresses))
    validator = phase_1_request_validator(round, sm_addresses)
    valid_requests = map(json.loads, filter(validator, requests))
    data = {}
    l_rem = []
    for r in valid_requests:
        data[r["id"]] = r["data"]
        l_rem.append(r["id"])
    return data, tuple(sorted(l_rem))

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

run_forever(
    9999,
    (("", 0), ("", 2)),
    RoundMetadata(1, now() + 10, 120, 60),
    500
)
