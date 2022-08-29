from time import time as now

def remaining_until(time: float):
    """Returns the time remaining in seconds, until a given second."""
    return max(time - now(), 0)
