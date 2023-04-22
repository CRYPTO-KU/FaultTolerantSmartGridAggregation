import random

from phe      import paillier
from simulate import link_utils, shared_mem, simulator, base_meta

CONSTANTS = {
    "K"                 : int(2e20),
    "PRF_KEY_LEN"       : 32,
    "PAILLIER_KEY_LEN"  : 256,
    "RUNS_PER_CONFIG"   : 1,
    "STARTUP_WAIT"      : 0.1,
    "PHASE_1_LEN"       : 1.0,
    "SEED"              : 0
}

# Set random seed
random.seed(CONSTANTS["SEED"])

print("SM COUNT,PRIVACY TYPE,P,Terminated,Success,DC TIME,MAX SM TIME,PHASE 1 COUNT,PHASE 2 COUNT")

for N in (50, 100, 200, 400):
    for PRIVACY_TYPE in ("mask", "encr"):
        for P in (0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4):
            N_MIN = 0.76 * N

            args = { **CONSTANTS, "ROUND_LEN": 0.1 * N }

            args = { **args, "SM_COUNT": N, "N_MIN": N_MIN, "PRIVACY_TYPE": PRIVACY_TYPE, "P": P }

            # Generate Keys
            prf_keys = tuple([random.randbytes(args["PRF_KEY_LEN"]) for _ in range(N)])
            pk, sk = paillier.generate_paillier_keypair(n_length = CONSTANTS["PAILLIER_KEY_LEN"])

            args = { **args, "prf_keys": prf_keys, "pk": pk, "sk": sk }

            # Helper functions
            base_dc_meta = base_meta.base_dc_masking_meta(args) if PRIVACY_TYPE == "mask" else base_meta.base_dc_paillier_meta(args)
            base_sm_meta = base_meta.base_sm_masking_meta(args) if PRIVACY_TYPE == "mask" else base_meta.base_sm_paillier_meta(args)
            def make_net_mngr():
                return shared_mem.make_shared_memory_net_mngr(N)

            n_configs = 1 if P == 0 else CONSTANTS["RUNS_PER_CONFIG"]

            reports = simulator.simulate(
                N,
                args["STARTUP_WAIT"],
                link_utils.uniform_fail_configurations(N, P, n_configs),
                make_net_mngr,
                base_dc_meta,
                base_sm_meta
            )

            for dc_report, sm_reports in reports:
                terminated  = int(not dc_report.terminated)
                success     = int(dc_report.success)
                dc_time     = dc_report.t_end - dc_report.t_start
                dc_time_p_1 = dc_report.t_phase_1 - dc_report.t_start
                max_sm_time = max([i.t_end - i.t_start for i in sm_reports])
                phase_1_cnt = dc_report.phase_1_count
                phase_2_cnt = dc_report.phase_2_count
                print(f"{N},{PRIVACY_TYPE},{P},{terminated},{success},{dc_time},{dc_time_p_1},{max_sm_time},{phase_1_cnt},{phase_2_cnt}")
