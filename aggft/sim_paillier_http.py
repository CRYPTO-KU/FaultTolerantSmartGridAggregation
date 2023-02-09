import threading

from os import urandom
from dataclasses import dataclass
from queue import Queue

from random import randint as random_int
from time import time as now
from itertools import combinations

import csv

from dc    import DC, make_dc
from sm    import SM, make_sm
from model import metadata
from util  import network

from phe import paillier

from typing import Tuple, Dict

SM_COUNT         = 2
K                = int(2e20)
PORT_LOWER_BOUND = 55555
PORT_UPPER_BOUND = 65535
N_MIN            = 2
STARTUP_WAIT     = 1
ROUND_LEN        = 4
PHASE_1_LEN      = 2
REPORT_FILENAME  = "report_3_sm.csv"

DC_PORT  = 8000
SM_PORTS = [ DC_PORT + i + 1 for i in range(SM_COUNT) ]

TOPOLOGY = {
    (-1, 0): True,
    (-1, 1): True,
    (0, 1): True,
}

pk, sk = paillier.generate_paillier_keypair()

topology = {}

for k, v in TOPOLOGY.items():
    a, b = k
    topology[(a, b)] = v
    topology[(b, a)] = v
    topology[(a, a)] = False
    topology[(b, b)] = False

prf_keys = [urandom(32) for _ in range(SM_COUNT)]

# report_head = ["Terminated?", "Aggregate Calculated?", "N_MIN Reached?", "Phase 1 Count", "Phase 2 Count", "DC Active Time", *map(lambda i: f"SM {i} Active Time", range(SM_COUNT))]
# report_rows = []

def dc_factory(test_start: float, c: Dict[Tuple[int, int], bool]) -> DC:
    dc_addr = network.Address("localhost", DC_PORT, True)

    sm_addr = []
    for i in range(SM_COUNT):
        sm_addr.append(network.Address("localhost", SM_PORTS[i], c[(-1, i)]))

    meta = metadata.DCPaillierMetadata(
        metadata.AGGFT_MODE.MASKING,
        dc_addr,
        sm_addr,
        N_MIN,
        test_start + STARTUP_WAIT,
        ROUND_LEN,
        PHASE_1_LEN,
        pk,
        sk
    )

    # Create network manager
    net_mngr = network.HTTPNetworkManager()

    return make_dc(meta, net_mngr)

def sm_factory(id: int, test_start: float, c: Dict[Tuple[int, int], bool]) -> SM:
    dc_addr = network.Address("localhost", DC_PORT, c[(-1, id)])

    sm_addr = []
    for i in range(SM_COUNT):
        sm_addr.append(network.Address("localhost", SM_PORTS[i], c[(id, i)]))

    meta = metadata.SMPaillierMetadata(
        metadata.AGGFT_MODE.MASKING,
        dc_addr,
        sm_addr,
        N_MIN,
        test_start + STARTUP_WAIT,
        ROUND_LEN,
        PHASE_1_LEN,
        pk
    )

    # Create network manager
    net_mngr = network.HTTPNetworkManager()

    return make_sm(id, meta, net_mngr)

test_start = now()

dc        = dc_factory(test_start, topology)
dc_thread = threading.Thread(target = dc.run_once)

dc_thread.start()

sms        = []
sm_threads = []
for id in range(SM_COUNT):
    sm        = sm_factory(id, test_start, topology)
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
