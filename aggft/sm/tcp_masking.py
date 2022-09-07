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

def run_forever(port: network.Port, dc_address: network.Address, id: int, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, k: int, prf_key: bytes):
    # Wait for the right time to start operation
    log.info("Waiting for operation start...")
    sleep(time.remaining_until(meta.start))
    log.info("Operation started.")
    log.info(f"Round {0} started.")
    run_single_round(0, port, dc_address, id, sm_addresses, meta, k, prf_key)
    log.info(f"Round {0} ended.")

def run_single_round(round: int, port: network.Port, dc_address: network.Address, id: int, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, k: int, prf_key: bytes):
    # Wait for the right time to start round
    round_start = meta.start + meta.round_len * round
    sleep(time.remaining_until(round_start + 1))
    s = secrets.randbelow(k)
    p = prf.PRF(prf_key, round)
    is_ok = run_phase_1(round, dc_address, id, meta, k, s, p)
    if not is_ok:
        log.warning(f"[round {round}] [phase 1] Could not send data to data concentrator. Aborting round...")
        return
    log.success(f"[round {round}] [phase 1] Sent data to data concentrator.")
    run_phase_2(round, port, dc_address, id, sm_addresses, meta, s, k)
    log.info(f"[round {round}] [phase 2] Phase done.")
    log.info(f"[round {round}] Ending round...")
    
def run_phase_1(round: int, dc_address: network.Address, id: int, meta: RoundMetadata, k: int, s: int, p: int) -> bool:
    round_start = meta.start + meta.round_len * round
    phase_1_end = round_start + meta.phase_1_len
    masked = (get_raw_measurement(round) + s + p) % k
    data = { "id": id, "round": round, "data": masked }
    return network.send(dc_address, json.dumps(data), phase_1_end, "<START>", "<END>")

# TODO: Don't use a constant
def get_raw_measurement(round: int):
    return 15

def run_phase_2(round: int, port: network.Port, dc_address: network.Address, id: int, sm_addresses: Tuple[network.Address, ...], meta: RoundMetadata, s: int, k: int):
    round_start = meta.start + meta.round_len * round
    phase_2_end = round_start + meta.round_len
    requests = network.listen_multiple(port, phase_2_end, "<START>", "<END>", phase_2_early_stopper(round, id, sm_addresses))
    validator = phase_2_request_validator(round, id, sm_addresses)
    valid_requests = list(map(json.loads, filter(validator, requests)))
    if len(valid_requests) == 0: return False
    log.info(f"[round {round}] [phase 2] Got activated.")
    data = valid_requests[0]
    l_rem = tuple(filter(lambda rem: rem != id, data["l_rem"]))
    l_act = (*data["l_act"], id)
    s_new = (s + data["s"]) % k
    while not is_last(l_rem, l_act, meta.n_min):
        if time.remaining_until(phase_2_end) == 0: return
        next_sm = l_rem[0]
        data = { "round": round, "s": s_new, "l_rem": l_rem, "l_act": l_act }
        is_ok = network.send(
            sm_addresses[next_sm],
            json.dumps(data),
            phase_2_end,
            "<START>", "<END>"
        )
        if is_ok: return
        l_rem = tuple(filter(lambda rem: rem != next_sm, l_rem))
    if len(l_rem) + len(l_act) >= meta.n_min:
        data = { "round": round, "s": s_new, "l_rem": l_rem, "l_act": l_act }
        network.send(
            dc_address,
            json.dumps(data),
            phase_2_end,
            "<START>", "<END>"
        )

def is_last(l_rem: Tuple[int, ...], l_act: Tuple[int, ...], n_min: int) -> bool:
    return len(l_rem) == 0 or len(l_rem) + len(l_act) < n_min

def phase_2_early_stopper(round: int, id: int, sm_addresses: Tuple[network.Address, ...]):
    validator = phase_2_request_validator(round, id, sm_addresses)
    def early_stopper(data: Tuple[str, ...]):
        for d in data:
            if validator(d): return True
        return False
    return early_stopper

def phase_2_request_validator(round: int, id: int, sm_addresses: Tuple[network.Address, ...]):
    def validator(data: str) -> bool:
        dict_includes_keys = lambda dict, keys: dict.keys() >= keys
        try:
            json_data = json.loads(data)
            if not dict_includes_keys(json_data, {"round", "s", "l_rem", "l_act"}): return False
            if json_data["round"] != round: return False
            if not isinstance(json_data["l_rem"], list): return False
            if not isinstance(json_data["l_act"], list): return False
            intersection = list(set(json_data["l_rem"]) & set(json_data["l_act"]))
            if len(intersection): return False
            for i in json_data["l_rem"]:
                if i not in range(len(sm_addresses)): return False
            for i in json_data["l_act"]:
                if i not in range(len(sm_addresses)): return False
                if i == id: return False
            return True
        except json.JSONDecodeError:
            return False
    return validator
