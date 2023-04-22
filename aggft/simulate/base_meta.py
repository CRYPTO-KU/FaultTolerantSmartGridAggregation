from model import metadata


################################################################################
# Helper Functions
################################################################################


def base_dc_masking_meta(args):
    def inner():
        return metadata.DCMaskingMetadata(
            metadata.AGGFT_MODE.MASKING,
            None,  # Will be set by the DC factory
            tuple(),  # Will be set by the DC factory
            args["N_MIN"],
            0,  # Will be set by the DC factory
            args["ROUND_LEN"],
            args["PHASE_1_LEN"],
            args["K"],
            args["prf_keys"],
        )

    return inner


def base_dc_paillier_meta(args):
    def inner():
        return metadata.DCPaillierMetadata(
            metadata.AGGFT_MODE.HOMOMORPHIC,
            None,  # Will be set by the DC factory
            tuple(),  # Will be set by the DC factory
            args["N_MIN"],
            0,  # Will be set by the DC factory
            args["ROUND_LEN"],
            args["PHASE_1_LEN"],
            args["pk"],
            args["sk"],
        )

    return inner


def base_sm_masking_meta(args):
    def inner(id: int):
        return metadata.SMMaskingMetadata(
            metadata.AGGFT_MODE.MASKING,
            None,  # Will be set by the DC factory
            tuple(),  # Will be set by the DC factory
            args["N_MIN"],
            0,  # Will be set by the DC factory
            args["ROUND_LEN"],
            args["PHASE_1_LEN"],
            args["K"],
            args["prf_keys"][id],
        )

    return inner


def base_sm_paillier_meta(args):
    def inner(_: int):
        return metadata.SMPaillierMetadata(
            metadata.AGGFT_MODE.HOMOMORPHIC,
            None,  # Will be set by the DC factory
            tuple(),  # Will be set by the DC factory
            args["N_MIN"],
            0,  # Will be set by the DC factory
            args["ROUND_LEN"],
            args["PHASE_1_LEN"],
            args["pk"],
        )

    return inner
