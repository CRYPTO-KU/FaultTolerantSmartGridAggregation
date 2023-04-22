from time import time as now


################################################################################
# Data Types
################################################################################


Time = float


################################################################################
# Utility Functions
################################################################################


# Returns the time remaining until a specific point in time (Unix Time).
def remaining_until(time: Time):
    return max(time - now(), 0)
