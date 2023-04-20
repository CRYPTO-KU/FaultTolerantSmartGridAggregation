from dataclasses import replace

from dc          import DC, make_dc
from sm          import SM, make_sm
from model       import metadata
from util        import network

from typing  import Tuple, Dict

################################################################################
# DC / SM Factories
################################################################################

def dc_factory(
    sm_count: int,
    test_start: float,
    startup_wait: float,
    base_meta: metadata.DCMaskingMetadata | metadata.DCPaillierMetadata,
    net_mngr: network.NetworkManager,
    connectivity_table: Dict[Tuple[int, int], bool]
) -> DC:

    # -1 is for the DC
    dc_addr = network.Address("localhost", -1, True)

    c = connectivity_table
    sm_addr = tuple([network.Address("localhost", i, c[(-1, i)]) for i in range(sm_count)])

    meta = replace(
        base_meta,
        dc_address = dc_addr,
        sm_addresses = sm_addr,
        t_start = test_start + startup_wait
    )

    return make_dc(meta, net_mngr)

def sm_factory(
    id: int,
    sm_count: int,
    test_start: float,
    startup_wait: float,
    base_meta: metadata.SMMaskingMetadata | metadata.SMPaillierMetadata,
    net_mngr: network.NetworkManager,
    connectivity_table: Dict[Tuple[int, int], bool]
) -> SM:

    c = connectivity_table

    # -1 is for the DC
    dc_addr = network.Address("localhost", -1, c[(-1, id)])

    sm_addr = tuple([network.Address("localhost", i, c[(id, i)]) for i in range(sm_count)])

    meta = replace(
        base_meta,
        dc_address = dc_addr,
        sm_addresses = sm_addr,
        t_start = test_start + startup_wait
    )

    return make_sm(id, meta, net_mngr)
