from dataclasses import dataclass
from enum        import Enum
from typing      import Tuple

from ..util      import network

################################################################################
# Data Types
################################################################################

class AGGFT_MODE(Enum):
    MASKING     = 0
    HOMOMORPHIC = 1

# AggFT Rounds Metadata
# Base class for the masking and homomorphic encryption versions.
# Don't use directly.
@dataclass(frozen = True)
class Metadata:
    # AggFT Mode Of Operation
    # Specifies if we are using masking or homomorphic encryption for security.
    mode         : AGGFT_MODE

    # Data Concentrator (DC) Address
    dc_address   : network.Address

    # Smart Meters (SMs) Addresses
    sm_addresses : Tuple[network.Address, ...]

    # Minimum Number Of Contributing Smart Meters
    # The information needed to recover the aggregate is only sent, if at least
    # n_min households contribute.
    n_min        : int

    # First Round Start Time
    # Time in seconds since the epoch as a floating point number.
    # This is commonly referred to as Unix time.
    t_start      : float

    # Round Length / Duration (Seconds)
    t_round_len  : float

    # Phase 1 Length / Duration (Seconds)
    # The length of phase 2 is determined by t_round_len and t_phase_1_len.
    t_phase_1_len: float

# AggFT Rounds Metadata
# Specific for using masking.
# Base class for the DC and SM versions.
# Don't use directly.
@dataclass(frozen = True)
class MaskingMetadata(Metadata):
    # TODO: Document this variable
    k: int

# AggFT Rounds Metadata
# Specific for a DC using masking.
@dataclass(frozen = True)
class DCMaskingMetadata(MaskingMetadata):
    # Pre-shared PRF Keys
    # The smart meters add a round-dependent pseudo-random number produced by a
    # Pseudo-Random Function (PRF) that is computable by the smart meters and
    # the data concentrator using pre-shared keys.
    # This makes a privacy breach more difficult for eavesdroppers but does not
    # prevent the computation of the sum.
    prf_keys: Tuple[bytes, ...]

# AggFT Rounds Metadata
# Specific for an SM using masking.
@dataclass(frozen = True)
class SMMaskingMetadata(MaskingMetadata):
    # Pre-shared PRF Key
    prf_key: bytes

################################################################################
# Data Validation
################################################################################

def is_valid_metadata(m: Metadata) -> bool:
    # At least 2 smart meters should contribute
    if m.n_min <= 1:
        return False

    # Should be a valid Unix timestamp
    if m.t_start < 0:
        return False

    # Should be a valid time duration
    if m.t_round_len <= 0:
        return False

    # Should be a valid time duration
    # It should also be shorter than the total round duration
    if m.t_phase_1_len <= 0 or m.t_phase_1_len >= m.t_round_len:
        return False

    return True

def is_valid_masking_metadata(m: MaskingMetadata) -> bool:
    # Should be a valid metadata
    if not is_valid_metadata(m):
        return False

    # Should be a valid modulus
    if m.k <= 1:
        return False

    return True

def is_valid_dc_masking_metadata(m: DCMaskingMetadata) -> bool:
    # Should be a valid masking metadata
    if not is_valid_masking_metadata(m):
        return False

    # Should have one pre-shared key per smart meter
    if len(m.prf_keys) != len(m.sm_addresses):
        return False

    return True

def is_valid_sm_masking_metadata(m: SMMaskingMetadata) -> bool:
    # Should be a valid masking metadata
    return is_valid_masking_metadata(m)
