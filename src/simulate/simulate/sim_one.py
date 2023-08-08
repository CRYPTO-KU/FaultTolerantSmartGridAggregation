import threading

from time import time as now

import aggft

from . import utils

################################################################################
# Simulation Logic
################################################################################


def simulate_one_mask(
    n,
    n_min,
    link_status,
    sm_status,
    startup_wait,
    round_len,
    phase_1_len,
    prf_key_len,
    masking_modulus,
):
    prf_keys = [aggft.crypto.generate_prf_key(prf_key_len) for _ in range(n)]

    base_dc_meta = utils.base_dc_masking_meta(
        n_min, round_len, phase_1_len, masking_modulus, prf_keys
    )

    base_sm_meta = utils.base_sm_masking_meta(
        n_min, round_len, phase_1_len, masking_modulus, prf_keys
    )

    return simulate_one(
        n, link_status, sm_status, startup_wait, base_dc_meta, base_sm_meta
    )


def simulate_one_homomorphic(
    n,
    n_min,
    link_status,
    sm_status,
    startup_wait,
    round_len,
    phase_1_len,
    homomorphic_key_len,
):
    sk, pk = aggft.crypto.generate_homomorphic_keypair(homomorphic_key_len)

    base_dc_meta = utils.base_dc_homomorphic_meta(n_min, round_len, phase_1_len, sk, pk)

    base_sm_meta = utils.base_sm_homomorphic_meta(n_min, round_len, phase_1_len, pk)

    return simulate_one(
        n, link_status, sm_status, startup_wait, base_dc_meta, base_sm_meta
    )


def simulate_one(n, link_status, sm_status, startup_wait, base_dc_meta, base_sm_meta):
    registry = utils.make_registry(n)

    test_start = now()

    dc = utils.dc_factory(
        n,
        test_start,
        startup_wait,
        base_dc_meta,
        utils.make_net_mngr(-1, registry, link_status, sm_status),
        link_status,
        sm_status,
    )
    dc_thread = threading.Thread(target=dc.run_once)

    sms = []
    sm_threads = []
    for id in range(n):
        # Don't create failed smart meters
        if not sm_status[id]:
            continue

        sm = utils.sm_factory(
            id,
            n,
            test_start,
            startup_wait,
            base_sm_meta(id),
            utils.make_net_mngr(id, registry, link_status, sm_status),
            link_status,
            sm_status,
        )
        sm_thread = threading.Thread(target=sm.run_once)
        sm_threads.append(sm_thread)
        sms.append(sm)

    # Start all threads
    dc_thread.start()
    for thread in sm_threads:
        thread.start()

    # Wait for DC thread
    dc_thread.join()
    for sm in sms:
        sm.killed = True
    for thread in sm_threads:
        thread.join()

    dc_report = dc.reports[0]

    sm_reports = []
    idx = 0
    for id in range(n):
        if sm_status[id]:
            sm_reports.append(sms[idx].reports[0])
            idx += 1
        else:
            sm_reports.append(None)

    return dc_report, tuple(sm_reports)
