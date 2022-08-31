from time import time as now

# Types

Time = float

def remaining_until(time: Time):
    return max(time - now(), 0)
