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
    t_start: float = 0

    # Phase 1 End Time (Unix Time)
    t_phase_1: float = 0

    # Round End Time (Unix Time)
    t_end: float = 0

    # Did the round terminate properly or no?
    terminated: bool = False

    # Did we calculate an aggregate or no?
    success: bool = False

    # Number of participating SMs in phase 1.
    phase_1_count: int = 0

    # Number of participating SMs in phase 2.
    phase_2_count: int = 0

    # Total network requests received by DC.
    net_rcv: int = 0

    # Total characters received over the network.
    net_rcv_size: int = 0

    # Total successful network requests sent by DC.
    net_snd_succ: int = 0

    # Total successful characters send over the network.
    net_snd_succ_size: int = 0

    # Total failed network requests sent by DC.
    net_snd_fail: int = 0

    # Total failed characters send over the network.
    net_snd_fail_size: int = 0


# Smart Meter (SM) Report
# SM generates such a report each round.
# Contains useful metrics about the round from the perspective of the SM.
@dataclass
class SMReport:
    # Round Start Time (Unix Time)
    t_start: float = 0

    # Round End Time (Unix Time)
    t_end: float = 0

    # Total network requests received by SM.
    net_rcv: int = 0

    # Total characters received over the network.
    net_rcv_size: int = 0

    # Total successful network requests sent by SM.
    net_snd_succ: int = 0

    # Total successful characters send over the network.
    net_snd_succ_size: int = 0

    # Total failed network requests sent by SM.
    net_snd_fail: int = 0

    # Total failed characters send over the network.
    net_snd_fail_size: int = 0
