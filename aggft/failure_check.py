import random

from phe      import paillier
from simulate import link_utils, shared_mem, simulator, base_meta

CONSTANTS = {
    "N_MIN"             : 2,
    "K"                 : int(2e20),
    "PRF_KEY_LEN"       : 32,
    "PAILLIER_KEY_LEN"  : 256,
    "ROUND_LEN"         : 5.0,
    "PHASE_1_LEN"       : 2.0,
    "STARTUP_WAIT"      : 0.1,
    "SEED"              : 0
}

# Set random seed
random.seed(CONSTANTS["SEED"])

print("PRIVACY TYPE,SM COUNT,FAILURES")

for N in ( 2, 3, 4 ):
    for PRIVACY_TYPE in ( "mask", "encr" ):
        args = { **CONSTANTS, "SM_COUNT": N, "PRIVACY_TYPE": PRIVACY_TYPE }

        # Generate Keys
        prf_keys = tuple([random.randbytes(args["PRF_KEY_LEN"]) for _ in range(N)])
        pk, sk = paillier.generate_paillier_keypair(n_length = CONSTANTS["PAILLIER_KEY_LEN"])

        args = { **args, "prf_keys": prf_keys, "pk": pk, "sk": sk }

        # Helper functions
        base_dc_meta = base_meta.base_dc_masking_meta(args) if PRIVACY_TYPE == "mask" else base_meta.base_dc_paillier_meta(args)
        base_sm_meta = base_meta.base_sm_masking_meta(args) if PRIVACY_TYPE == "mask" else base_meta.base_sm_paillier_meta(args)
        def make_net_mngr():
            return shared_mem.make_shared_memory_net_mngr(N)

        reports = simulator.simulate(
            N,
            args["STARTUP_WAIT"],
            link_utils.all_links_configurations(N),
            make_net_mngr,
            base_dc_meta,
            base_sm_meta
        )

        failures = 0
        for dc_report, sm_reports in reports:
            failures += int(not dc_report.terminated)

        print(f"{PRIVACY_TYPE},{N},{failures}")
