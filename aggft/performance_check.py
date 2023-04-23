import random

from phe import paillier
from simulate import base_meta, link_utils, shared_mem, simulator
from util import network

################################################################################
# Simulation Parameters
################################################################################


# NOTE:
# Using HTTP with a large number of smart meters might not work due to OS
# limitations.

CONSTANTS = {
    "N_VALUES": (50, 100, 200, 400),
    "PRIVACY_TYPES": ("mask", "encr"),
    "P_VALUES": (0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4),
    "N_MIN_F": lambda N: 0.76 * N,
    "ROUND_LEN_F": lambda N: 0.1 * N,
    "K": int(2e20),
    "PRF_KEY_LEN": 32,
    "PAILLIER_KEY_LEN": 256,
    "RUNS_PER_CONFIG": 1,
    "STARTUP_WAIT": 0.1,
    "PHASE_1_LEN": 1.0,
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

print(
    "SM COUNT,PRIVACY TYPE,P,Terminated,Success,TOTAL DC TIME,PHASE 1 DC TIME,MAX TOTAL SM TIME,PHASE 1 COUNT,PHASE 2 COUNT,DC NET SND,DC NET RCV,MAX SM NET SND,MAX SM NET RCV"
)

for N in CONSTANTS["N_VALUES"]:
    for PRIVACY_TYPE in CONSTANTS["PRIVACY_TYPES"]:
        for P in CONSTANTS["P_VALUES"]:
            N_MIN = CONSTANTS["N_MIN_F"](N)
            ROUND_LEN = CONSTANTS["ROUND_LEN_F"](N)

            args = {
                **CONSTANTS,
                "SM_COUNT": N,
                "N_MIN": N_MIN,
                "PRIVACY_TYPE": PRIVACY_TYPE,
                "P": P,
                "ROUND_LEN": ROUND_LEN,
            }

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

            n_configs = 1 if P == 0 else CONSTANTS["RUNS_PER_CONFIG"]

            reports = simulator.simulate(
                N,
                args["STARTUP_WAIT"],
                link_utils.uniform_fail_configurations(N, P, n_configs),
                make_net_mngr,
                base_dc_meta,
                base_sm_meta,
                args["STARTING_PORT"],
            )

            for dc_report, sm_reports in reports:
                terminated = int(dc_report.terminated)
                success = int(dc_report.success)
                dc_time = dc_report.t_end - dc_report.t_start
                dc_time_p_1 = dc_report.t_phase_1 - dc_report.t_start
                max_sm_time = max([i.t_end - i.t_start for i in sm_reports])
                phase_1_cnt = dc_report.phase_1_count
                phase_2_cnt = dc_report.phase_2_count
                dc_net_snd = dc_report.net_snd_size
                dc_net_rcv = dc_report.net_rcv_size
                max_sm_snd = max([i.net_snd_size for i in sm_reports])
                max_sm_rcv = max([i.net_rcv_size for i in sm_reports])
                print(
                    f"{N},{PRIVACY_TYPE},{P},{terminated},{success},{dc_time},{dc_time_p_1},{max_sm_time},{phase_1_cnt},{phase_2_cnt},{dc_net_snd},{dc_net_rcv},{max_sm_snd},{max_sm_rcv}"
                )
