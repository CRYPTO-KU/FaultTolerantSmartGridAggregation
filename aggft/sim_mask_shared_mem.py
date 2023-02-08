import threading

from os import urandom
from dataclasses import dataclass
from queue import Queue

from random import randint as random_int
from time import time as now
from itertools import combinations

import csv

from dc    import DC, make_dc
from sm    import SM
from model import metadata
from util  import network

from collections import defaultdict

from typing import Tuple, Dict

SM_COUNT         = 2
K                = int(2e20)
PORT_LOWER_BOUND = 55555
PORT_UPPER_BOUND = 65535
N_MIN            = 2
STARTUP_WAIT     = 0.1
ROUND_LEN        = 4
PHASE_1_LEN      = 2
REPORT_FILENAME  = "report_3_sm.csv"

# Yield all combinations of elements from the input iterable
def all_combinations(iterable):
    for r in range(len(iterable) + 1):
        for c in combinations(iterable, r):
            yield c

def all_links(sm_count: int) -> Tuple[Tuple[int, int], ...]:
    links = []
    # -1 is for the DC
    for i in [-1] + list(range(sm_count)):
        for j in range(i + 1, sm_count):
            links.append((i, j))
    return tuple(links)

def all_links_validity_combinations(sm_count: int):
    links = all_links(sm_count)
    for c in all_combinations(links):
        v_comb = defaultdict(lambda: False)
        for i, j in c:
            v_comb[(i, j)] = True
            v_comb[(j, i)] = True
        for i in [-1] + list(range(sm_count)):
            v_comb[(i, i)] = False
        yield v_comb

prf_keys = [urandom(32) for i in range(SM_COUNT)]

# report_head = ["Terminated?", "Aggregate Calculated?", "N_MIN Reached?", "Phase 1 Count", "Phase 2 Count", "DC Active Time", *map(lambda i: f"SM {i} Active Time", range(SM_COUNT))]
# report_rows = []

def dc_factory(test_start: float, registry: Dict[Tuple[network.Host, network.Port], Queue], c: Dict[Tuple[int, int], bool]) -> DC:
    # -1 is for the DC
    dc_addr = network.Address("localhost", -1, True)

    sm_addr = []
    for i in range(SM_COUNT):
        sm_addr.append(network.Address("localhost", i, c[(-1, i)]))

    meta = metadata.DCMaskingMetadata(
        metadata.AGGFT_MODE.MASKING,
        dc_addr,
        sm_addr,
        N_MIN,
        test_start + STARTUP_WAIT,
        ROUND_LEN,
        PHASE_1_LEN,
        K,
        prf_keys
    )

    # Create network manager
    net_mngr = network.SharedMemoryNetworkManager(registry)

    return make_dc(meta, net_mngr)

def sm_factory(id: int, test_start: float, registry: Dict[Tuple[network.Host, network.Port], Queue], c: Dict[Tuple[int, int], bool]) -> SM:
    # -1 is for the DC
    dc_addr = network.Address("localhost", -1, c[(-1, id)])

    sm_addr = []
    for i in range(SM_COUNT):
        sm_addr.append(network.Address("localhost", i, c[(id, i)]))

    meta = metadata.SMMaskingMetadata(
        metadata.AGGFT_MODE.MASKING,
        dc_addr,
        sm_addr,
        N_MIN,
        test_start + STARTUP_WAIT,
        ROUND_LEN,
        PHASE_1_LEN,
        K,
        prf_keys[id]
    )

    # Create network manager
    net_mngr = network.SharedMemoryNetworkManager(registry)

    return SM(id, meta, net_mngr)

for c in all_links_validity_combinations(SM_COUNT):
    # Create registry for shared memory network manager
    registry = {}
    for i in [-1] + list(range(SM_COUNT)):
        registry[("localhost", i)] = Queue()

    test_start = now()

    dc        = dc_factory(test_start, registry, c)
    dc_thread = threading.Thread(target = dc.run_once)

    dc_thread.start()

    sms        = []
    sm_threads = []
    for id in range(SM_COUNT):
        sm        = sm_factory(id, test_start, registry, c)
        sm_thread = threading.Thread(target = sm.run_once)
        sm_thread.start()
        sms.append(sm)
        sm_threads.append(sm_thread)

    # Wait until all threads terminate
    threads = [dc_thread] + sm_threads
    for thread in threads:
        thread.join()

    # durations = (dc_test_data["duration"], *list(map(lambda sm_test_data: sm_test_data["duration"], sm_test_datas)))
    # report_rows.append([
    #     dc_test_data["terminated"],
    #     dc_test_data["success"],
    #     dc_test_data["n_min_reached"],
    #     dc_test_data["phase_1_count"],
    #     dc_test_data["phase_2_count"],
    #     *map(lambda d: str(round(d, 2)), durations)
    # ])

    print("\n\n\n\n")

# with open(REPORT_FILENAME, "w") as csv_file: 
#     csv_writer = csv.writer(csv_file) 
#     csv_writer.writerow(report_head) 
#     csv_writer.writerows(report_rows)
