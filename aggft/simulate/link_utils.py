from itertools   import combinations
from random      import random

from collections import defaultdict

from typing      import Tuple

################################################################################
# Private Internals
################################################################################

# Yield all combinations of elements from the input iterable
def _all_combinations(iterable):
    for r in range(len(iterable) + 1):
        for c in combinations(iterable, r):
            yield c

# Generate all possible links for a given SM count
# Includes links to DC
def _all_links(sm_count: int) -> Tuple[Tuple[int, int], ...]:
    links = []
    # -1 is for the DC
    for i in [-1] + list(range(sm_count)):
        for j in range(i + 1, sm_count):
            links.append((i, j))
    return tuple(links)

# Generate a configuration where the links fail with probability p
def _uniform_fail_configuration(sm_count: int, p: float):
    links = _all_links(sm_count)
    connectivity_table = defaultdict(lambda: False)
    for i, j in links:
        is_connected = random() >= p
        connectivity_table[(i, j)] = is_connected
        connectivity_table[(j, i)] = is_connected
    for i in [-1] + list(range(sm_count)):
        connectivity_table[(i, i)] = False
    return connectivity_table

################################################################################
# Links Helpers
################################################################################

def all_links_configurations(sm_count: int):
    links = _all_links(sm_count)
    for c in _all_combinations(links):
        connectivity_table = defaultdict(lambda: False)
        for i, j in c:
            connectivity_table[(i, j)] = True
            connectivity_table[(j, i)] = True
        for i in [-1] + list(range(sm_count)):
            connectivity_table[(i, i)] = False
        yield connectivity_table

def uniform_fail_configurations(sm_count: int, f: float, n: int):
    for _ in range(n):
        yield _uniform_fail_configuration(sm_count, f)
