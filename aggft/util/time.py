from time import time as now

def remaining_until(time: float):
    return max(time - now(), 0)
