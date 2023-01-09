from dataclasses import dataclass

################################################################################
# Data Types
################################################################################

@dataclass
class DCReport:
    t_start      : float
    t_end        : float = 0
    terminated   : bool  = False
    success      : bool  = False
    phase_1_count: int   = 0
    phase_2_count: int   = 0
    net_rcv      : int   = 0
    net_snd      : int   = 0

@dataclass
class SMReport:
    t_start: float
    t_end  : float = 0
    net_rcv: int   = 0
    net_snd: int   = 0
