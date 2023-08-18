import random

from dataclasses import replace
from queue import Queue
from typing import Dict, List, Tuple

from aggft import sm, dc, metadata, network

################################################################################
# Shared Memory Networking Helpers
################################################################################


def make_registry(sm_count: int) -> network.Registry:
    registry = {}
    for i in range(-1, sm_count):
        registry[("localhost", i)] = Queue()
    return registry


def make_net_mngr(
    id, registry: network.Registry, link_status, sm_status
) -> network.SharedMemoryNetworkManager:
    return network.SharedMemoryNetworkManager(id, registry, link_status, sm_status)


################################################################################
# Failures Helpers
################################################################################


def generate_link_status(
    n, dc_link_fail_prob, sm_link_fail_prob, dc_link_fail_exact, sm_link_fail_exact
):
    status = {}

    # DC Links
    if dc_link_fail_exact:
        dc_link_fails = int(dc_link_fail_prob * n)
        dc_link_status = [False] * dc_link_fails + [True] * (n - dc_link_fails)
        random.shuffle(dc_link_status)
    else:
        dc_link_status = [
            False if random.random() <= dc_link_fail_prob else True for _ in range(n)
        ]

    for i in range(0, n):
        status[(i, -1)] = status[(-1, i)] = dc_link_status[i]

    # SM Links
    sm_link_count = int(n * (n - 1) / 2)
    if sm_link_fail_exact:
        sm_link_fails = int(sm_link_fail_prob * sm_link_count)
        sm_link_status = [False] * sm_link_fails + [True] * (
            sm_link_count - sm_link_fails
        )
        random.shuffle(sm_link_status)
    else:
        sm_link_status = [
            False if random.random() <= sm_link_fail_prob else True
            for _ in range(sm_link_count)
        ]

    sm_link_idx = 0
    for i in range(0, n):
        for j in range(i + 1, n):
            status[(i, j)] = status[(j, i)] = sm_link_status[sm_link_idx]
            sm_link_idx += 1

    # No Loops
    for i in range(-1, n):
        status[(i, i)] = False

    return status


def generate_sm_status(n, sm_full_fail_prob, sm_full_fail_exact):
    if not sm_full_fail_exact:
        return [
            False if random.random() <= sm_full_fail_prob else True for _ in range(n)
        ]

    sm_fails = int(sm_full_fail_prob * n)
    sm_status = [False] * sm_fails + [True] * (n - sm_fails)
    random.shuffle(sm_status)

    return sm_status


################################################################################
# Base Metadata
################################################################################


def base_dc_masking_meta(n_min, round_len, phase_1_len, masking_modulus, prf_keys):
    return metadata.DCMaskingMetadata(
        metadata.AGGFT_MODE.MASKING,
        None,  # Will be set by the DC factory
        tuple(),  # Will be set by the DC factory
        n_min,
        0,  # Will be set by the DC factory
        round_len,
        phase_1_len,
        masking_modulus,
        prf_keys,
    )


def base_sm_masking_meta(n_min, round_len, phase_1_len, masking_modulus, prf_keys):
    def inner(id: int):
        return metadata.SMMaskingMetadata(
            metadata.AGGFT_MODE.MASKING,
            None,  # Will be set by the DC factory
            tuple(),  # Will be set by the DC factory
            n_min,
            0,  # Will be set by the DC factory
            round_len,
            phase_1_len,
            masking_modulus,
            prf_keys[id],
        )

    return inner


def base_dc_homomorphic_meta(n_min, round_len, phase_1_len, sk, pk):
    return metadata.DCHomomorphicMetadata(
        metadata.AGGFT_MODE.HOMOMORPHIC,
        None,  # Will be set by the DC factory
        tuple(),  # Will be set by the DC factory
        n_min,
        0,  # Will be set by the DC factory
        round_len,
        phase_1_len,
        pk,
        sk,
    )


def base_sm_homomorphic_meta(n_min, round_len, phase_1_len, pk):
    def inner(_: int):
        return metadata.SMHomomorphicMetadata(
            metadata.AGGFT_MODE.HOMOMORPHIC,
            None,  # Will be set by the DC factory
            tuple(),  # Will be set by the DC factory
            n_min,
            0,  # Will be set by the DC factory
            round_len,
            phase_1_len,
            pk,
        )

    return inner


################################################################################
# DC / SM Factories
################################################################################


def dc_factory(
    n: int,
    test_start: float,
    startup_wait: float,
    base_meta: metadata.DCMaskingMetadata | metadata.DCHomomorphicMetadata,
    net_mngr: network.NetworkManager,
    link_status: Dict[Tuple[int, int], bool],
    sm_status: List[bool],
    link_valid,
) -> dc.DC:
    dc_addr = network.Address("localhost", -1, link_valid[(-1, -1)])

    sm_addr = tuple([network.Address("localhost", i, link_valid[(-1, i)]) for i in range(n)])

    meta = replace(
        base_meta,
        dc_address=dc_addr,
        sm_addresses=sm_addr,
        t_start=test_start + startup_wait,
    )

    return dc.make_dc(meta, net_mngr)


def sm_factory(
    id: int,
    n: int,
    test_start: float,
    startup_wait: float,
    base_meta: metadata.SMMaskingMetadata | metadata.SMHomomorphicMetadata,
    net_mngr: network.NetworkManager,
    link_status: Dict[Tuple[int, int], bool],
    sm_status: List[bool],
    link_valid,
) -> sm.SM:
    dc_addr = network.Address("localhost", -1, link_valid[(id, -1)])

    sm_addr = tuple([network.Address("localhost", i, link_valid[(id, i)]) for i in range(n)])

    meta = replace(
        base_meta,
        dc_address=dc_addr,
        sm_addresses=sm_addr,
        t_start=test_start + startup_wait,
    )

    return sm.make_sm(id, meta, net_mngr)
