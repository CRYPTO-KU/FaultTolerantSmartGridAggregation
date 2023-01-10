from dataclasses import dataclass

################################################################################
# Data Types
################################################################################

# Data Concentrator (DC) Report
# DC generates such a report each round.
# Contains useful metrics about the round from the perspective of the DC.
@dataclass
class DCReport:
    t_start      : float = 0
    t_end        : float = 0
    terminated   : bool  = False
    success      : bool  = False
    phase_1_count: int   = 0
    phase_2_count: int   = 0
    net_rcv      : int   = 0
    net_snd      : int   = 0

# Smart Meter (SM) Report
# SM generates such a report each round.
# Contains useful metrics about the round from the perspective of the SM.
@dataclass
class SMReport:
    t_start: float = 0
    t_end  : float = 0
    net_rcv: int   = 0
    net_snd: int   = 0
