# Standard Library Imports

import threading

from os import urandom
from random import randint as random_int
from time import time as now

import csv

# Project Imports

from aggft.dc import tcp_masking as dc
from aggft.sm import tcp_masking as sm

from aggft.model.round import RoundMetadata

# Standard Library Type Imports

from typing import Tuple

SM_COUNT = 3
K = int(2e20)
PORT_LOWER_BOUND = 55555
PORT_UPPER_BOUND = 65535
N_MIN = 1
STARTUP_WAIT = 0.1
ROUND_LEN = 4
PHASE_1_LEN = 2
REPORT_FILENAME = "report_3_sm.csv"

def generate_port_numbers(n: int) -> Tuple[int, ...]:
    ports = ()
    while len(ports) < n:
        r = random_int(PORT_LOWER_BOUND, PORT_UPPER_BOUND)
        if r not in ports: ports = (*ports, r)
    return ports


def all_links(n):
    links = []
    for i in range(n):
        for j in range(i + 1, n):
            links.append(f"{i}-{j}")
    return links

def all_links_combinations(n):
    links = all_links(n)
    combination = list(map(lambda _: False, links))
    yield dict(zip(links, combination))
    for i in range(2 ** len(links) - 1):
        if i % 2 == 0:
            combination[-1] = not combination[-1]
        else:
            for j in range(len(links) - 1, -1, -1):
                if combination[j] == True:
                    combination[j - 1] = not combination[j - 1]
                    break
        yield dict(zip(links, combination))

prf_key = urandom(32)
ports = generate_port_numbers(SM_COUNT + 1)
dc_port = ports[0]
sm_ports = ports[1:]

dc_address = ("localhost", dc_port)
sm_addresses = tuple(map(lambda port: ("localhost", port), sm_ports))

report_head = ["Terminated?", "Aggregate Calculated?", "N_MIN Reached?", "Phase 1 Count", "Phase 2 Count", "DC Active Time", *map(lambda i: f"SM {i} Active Time", range(SM_COUNT))]
report_rows = []

for c in all_links_combinations(SM_COUNT + 1):
    test_start = now()
    meta = RoundMetadata(N_MIN, test_start + STARTUP_WAIT, ROUND_LEN, PHASE_1_LEN)

    dc_test_data = {}
    combination_sm_addresses = []
    for i, a in enumerate(sm_addresses):
        combination_sm_addresses.append((a, c[f"0-{i + 1}"]))
    combination_sm_addresses = tuple(combination_sm_addresses)

    dc_thread = threading.Thread(
        target = dc.run_forever,
        args = (dc_port, combination_sm_addresses, meta, K, prf_key, dc_test_data)
    )
    dc_thread.start()

    sm_test_datas = ()
    sm_threads = ()

    for id in range(SM_COUNT):
        sm_test_data = {}
        sm_test_datas = (*sm_test_datas, sm_test_data)
        combination_dc_address = (dc_address, c[f"0-{id + 1}"])
        combination_sm_addresses = []
        for i, a in enumerate(sm_addresses):
            combination_sm_addresses.append((a, c[f"{min(id, i) + 1}-{max(id, i) + 1}"] if i != id else True))
        combination_sm_addresses = tuple(combination_sm_addresses)
        sm_thread = threading.Thread(
            target = sm.run_forever,
            args = (sm_ports[id], combination_dc_address, id, combination_sm_addresses, meta, K, prf_key, sm_test_data)
        )
        sm_thread.start()
        sm_threads = (*sm_threads, sm_thread)

    # Wait until all threads terminate
    threads = (dc_thread, *sm_threads)
    for thread in threads:
        thread.join()

    durations = (dc_test_data["duration"], *list(map(lambda sm_test_data: sm_test_data["duration"], sm_test_datas)))
    report_rows.append([
        dc_test_data["terminated"],
        dc_test_data["success"],
        dc_test_data["n_min_reached"],
        dc_test_data["phase_1_count"],
        dc_test_data["phase_2_count"],
        *map(lambda d: str(round(d, 2)), durations)
    ])

with open(REPORT_FILENAME, "w") as csv_file: 
    csv_writer = csv.writer(csv_file) 
    csv_writer.writerow(report_head) 
    csv_writer.writerows(report_rows)
