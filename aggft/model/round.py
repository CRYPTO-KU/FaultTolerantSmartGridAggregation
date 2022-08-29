from dataclasses import dataclass

@dataclass(frozen = True)
class RoundMetadata:
    n_min: int
    start: float
    round_len: float
    phase_1_len: float
