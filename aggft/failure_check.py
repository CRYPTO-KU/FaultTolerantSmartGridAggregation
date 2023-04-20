from os       import urandom
from phe      import paillier
from simulate import link_utils, shared_mem, simulator, args, base_meta

K           = int(2e20)
PRF_KEY_LEN = 32

# Parse arguments
argv = args.parse_args()

# Generate Keys
prf_keys = tuple([urandom(PRF_KEY_LEN) for _ in range(argv.SM_COUNT)])
pk, sk = paillier.generate_paillier_keypair()

# Helper functions
base_dc_meta = base_meta.base_dc_masking_meta(argv, K, prf_keys) if argv.PRIVACY_TYPE == "mask" else base_meta.base_dc_paillier_meta(argv, pk, sk)
base_sm_meta = base_meta.base_sm_masking_meta(argv, K, prf_keys) if argv.PRIVACY_TYPE == "mask" else base_meta.base_sm_paillier_meta(argv, pk)
def make_net_mngr():
    return shared_mem.make_shared_memory_net_mngr(argv.SM_COUNT)

reports = simulator.simulate(
    argv.SM_COUNT,
    argv.STARTUP_WAIT,
    link_utils.all_links_configurations(argv.SM_COUNT),
    make_net_mngr,
    base_dc_meta,
    base_sm_meta
)

failures = 0
for dc_report, sm_reports in reports:
    failures += int(not dc_report.terminated)

print(f"{argv.PRIVACY_TYPE},{argv.SM_COUNT},{failures}")
