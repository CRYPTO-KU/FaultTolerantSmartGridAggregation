from dataclasses import dataclass

################################################################################
# Data Types
################################################################################

# Data Concentrator (DC) Report
# DC generates such a report each round.
# Contains useful metrics about the round from the perspective of the DC.
@dataclass
class DCReport:
    # Round Start Time
    # Time in seconds since the epoch as a floating point number.
    # This is commonly referred to as Unix time.
    t_start      : float = 0

    # Round End Time (Unix Time)
    t_end        : float = 0

    # Did the round terminate properly or no?
    terminated   : bool  = False

    # Did we calculate an aggregate or no?
    success      : bool  = False

    # Number of participating SMs in phase 1.
    phase_1_count: int   = 0

    # Number of participating SMs in phase 2.
    phase_2_count: int   = 0

    # Total network requests received by DC.
    net_rcv      : int   = 0

    # Total network requests sent by DC.
    net_snd      : int   = 0

# Smart Meter (SM) Report
# SM generates such a report each round.
# Contains useful metrics about the round from the perspective of the SM.
@dataclass
class SMReport:
    # Round Start Time (Unix Time)
    t_start: float = 0

    # Round End Time (Unix Time)
    t_end  : float = 0

    # Total network requests received by SM.
    net_rcv: int   = 0

    # Total network requests sent by SM.
    net_snd: int   = 0