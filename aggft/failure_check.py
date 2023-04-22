import random

from phe import paillier
from simulate import base_meta, link_utils, shared_mem, simulator
from util import network


################################################################################
# Simulation Parameters
################################################################################


CONSTANTS = {
    "N_VALUES": (2, 3, 4),
    "PRIVACY_TYPES": ("mask", "encr"),
    "N_MIN": 2,
    "K": int(2e20),
    "PRF_KEY_LEN": 32,
    "PAILLIER_KEY_LEN": 256,
    "ROUND_LEN": 5.0,
    "PHASE_1_LEN": 2.0,
    "STARTUP_WAIT": 0.1,
    "SEED": 0,
    "USE_HTTP": False,
    "HTTP_STARTING_PORT": 9000,
}


################################################################################
# Simulation Logic
################################################################################


# Set random seed
random.seed(CONSTANTS["SEED"])

# Set starting port
CONSTANTS["STARTING_PORT"] = (
    CONSTANTS["HTTP_STARTING_PORT"] if CONSTANTS["USE_HTTP"] else -1
)

# CSV header
print("PRIVACY TYPE,SM COUNT,FAILURES")

for N in CONSTANTS["N_VALUES"]:
    for PRIVACY_TYPE in CONSTANTS["PRIVACY_TYPES"]:
        args = {**CONSTANTS, "SM_COUNT": N, "PRIVACY_TYPE": PRIVACY_TYPE}

        # Generate Keys
        prf_keys = tuple([random.randbytes(args["PRF_KEY_LEN"]) for _ in range(N)])
        pk, sk = paillier.generate_paillier_keypair(
            n_length=CONSTANTS["PAILLIER_KEY_LEN"]
        )

        args = {**args, "prf_keys": prf_keys, "pk": pk, "sk": sk}

        registry = None if CONSTANTS["USE_HTTP"] else shared_mem.make_registry(N)

        # Helper functions
        base_dc_meta = (
            base_meta.base_dc_masking_meta(args)
            if PRIVACY_TYPE == "mask"
            else base_meta.base_dc_paillier_meta(args)
        )
        base_sm_meta = (
            base_meta.base_sm_masking_meta(args)
            if PRIVACY_TYPE == "mask"
            else base_meta.base_sm_paillier_meta(args)
        )

        def make_net_mngr():
            if CONSTANTS["USE_HTTP"]:
                return network.HTTPNetworkManager()
            return network.SharedMemoryNetworkManager(registry)

        reports = simulator.simulate(
            N,
            args["STARTUP_WAIT"],
            link_utils.all_links_configurations(N),
            make_net_mngr,
            base_dc_meta,
            base_sm_meta,
            args["STARTING_PORT"],
        )

        failures = 0
        for dc_report, sm_reports in reports:
            failures += int(not dc_report.terminated)

        # CSV row
        print(f"{PRIVACY_TYPE},{N},{failures}")
