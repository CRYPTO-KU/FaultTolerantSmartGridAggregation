# Standard Library Imports

import threading

from os import urandom
from random import randint as random_int
from time import time as now

# Project Imports

from aggft.dc import tcp_masking as dc
from aggft.sm import tcp_masking as sm

from aggft.model.round import RoundMetadata

# Standard Library Type Imports

from typing import Tuple

SM_COUNT = 2
K = int(2e20)
PORT_LOWER_BOUND = 55555
PORT_UPPER_BOUND = 65535
N_MIN = 1
STARTUP_WAIT = 3
ROUND_LEN = 10
PHASE_1_LEN = 5

def generate_port_numbers(n: int) -> Tuple[int, ...]:
    ports = ()
    while len(ports) < n:
        r = random.randint(PORT_LOWER_BOUND, PORT_UPPER_BOUND)
        if r not in ports: ports = (*ports, r)
    return ports

script_start = now()
prf_key = os.urandom(32)
ports = generate_port_numbers(SM_COUNT + 1)
dc_port = ports[0]
sm_ports = ports[1:]
dc_address = ("localhost", dc_port)
sm_addresses = tuple(map(lambda port: ("localhost", port), sm_ports))
meta = RoundMetadata(N_MIN, script_start + STARTUP_WAIT, ROUND_LEN, PHASE_1_LEN)

thread_dc = threading.Thread(
    target = dc.run_forever,
    args = (dc_port, sm_addresses, meta, K, prf_key)
)
thread_dc.start()

for id in range(SM_COUNT):
    thread_sm = threading.Thread(
        target = sm.run_forever,
        args = (sm_ports[id], dc_address, id, sm_addresses, meta, K, prf_key)
    )
    thread_sm.start()
