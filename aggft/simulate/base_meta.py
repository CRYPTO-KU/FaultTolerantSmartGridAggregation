from model import metadata


################################################################################
# Helper Functions
################################################################################


def base_dc_masking_meta(argv, K, prf_keys):
    def inner():
        return metadata.DCMaskingMetadata(
            metadata.AGGFT_MODE.MASKING,
            None, # Will be set by the DC factory
            tuple(), # Will be set by the DC factory
            argv.N_MIN,
            0, # Will be set by the DC factory
            argv.ROUND_LEN,
            argv.PHASE_1_LEN,
            K,
            prf_keys
        )
    return inner

def base_dc_paillier_meta(argv, pk, sk):
    def inner():
        return metadata.DCPaillierMetadata(
            metadata.AGGFT_MODE.HOMOMORPHIC,
            None, # Will be set by the DC factory
            tuple(), # Will be set by the DC factory
            argv.N_MIN,
            0, # Will be set by the DC factory
            argv.ROUND_LEN,
            argv.PHASE_1_LEN,
            pk,
            sk
        )
    return inner

def base_sm_masking_meta(argv, K, prf_keys):
    def inner (id: int):
        return metadata.SMMaskingMetadata(
            metadata.AGGFT_MODE.MASKING,
            None, # Will be set by the DC factory
            tuple(), # Will be set by the DC factory
            argv.N_MIN,
            0, # Will be set by the DC factory
            argv.ROUND_LEN,
            argv.PHASE_1_LEN,
            K,
            prf_keys[id]
        )
    return inner

def base_sm_paillier_meta(argv, pk):
    def inner (_: int):
        return metadata.SMPaillierMetadata(
            metadata.AGGFT_MODE.HOMOMORPHIC,
            None, # Will be set by the DC factory
            tuple(), # Will be set by the DC factory
            argv.N_MIN,
            0, # Will be set by the DC factory
            argv.ROUND_LEN,
            argv.PHASE_1_LEN,
            pk
        )
    return inner
