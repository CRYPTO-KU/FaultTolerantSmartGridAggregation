import argparse, json, random

from itertools import product

import aggft

from .report import report
from .validate import validate_fig_spec as validate_spec
from .sim_one import simulate_one_mask, simulate_one_homomorphic


def main():
    args = parse_args()
    spec = get_spec(args)

    validate_spec(spec)

    random.seed(spec["random-seed"])

    simulate(spec)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run AggFT simulations for figure 1 in the paper."
    )

    parser.add_argument(
        "spec",
        type=argparse.FileType("r"),
        help=f"Path to the JSON specification file.",
    )

    return parser.parse_args()


def get_spec(args):
    return json.loads(args.spec.read())


def simulate(spec):
    if "mask" in spec["privacy-types"]:
        masking_modulus = spec["masking-modulus"]
        prf_key_len = spec["prf-key-len"]

    if "encr" in spec["privacy-types"]:
        homomorphic_key_len = spec["homomorphic-key-len"]

    n = 4
    startup_wait = spec["startup-wait"]
    round_len = spec["round-len"]
    phase_1_len = spec["phase-1-len"]
    n_min_const = "N/A"
    n_min = spec["n-min"]
    failure_probs = ["N/A"] * 3
    failure_exact = ["N/A"] * 3
    round_len = spec["round-len"]
    phase_1_len = spec["phase-1-len"]
    sm_status, link_status, link_valid = fig_topology()

    for privacy_type in spec["privacy-types"]:
        for _ in range(spec["simulations-per-config"]):
            if privacy_type == "mask":
                dc_report, sm_reports = simulate_one_mask(
                    n,
                    n_min,
                    link_status,
                    sm_status,
                    startup_wait,
                    round_len,
                    phase_1_len,
                    prf_key_len,
                    masking_modulus,
                    link_valid,
                )
            else:
                dc_report, sm_reports = simulate_one_homomorphic(
                    n,
                    n_min,
                    link_status,
                    sm_status,
                    startup_wait,
                    round_len,
                    phase_1_len,
                    homomorphic_key_len,
                    link_valid,
                )

            report(
                n,
                n_min_const,
                n_min,
                privacy_type,
                *failure_probs,
                *failure_exact,
                link_status,
                sm_status,
                dc_report,
                sm_reports,
            )


def fig_topology():
    n = 4
    sm_status = [True] * n
    link_status = {}
    link_valid = {}

    # Links to DC
    for i in range(0, n):
        link_status[(i, -1)] = link_status[(-1, i)] = True
    # All working but one
    link_status[(3, -1)] = link_status[(-1, 3)] = False

    # Links between SMs
    for i in range(0, n):
        for j in range(i + 1, n):
            link_status[(i, j)] = link_status[(j, i)] = False
    # All failed but four
    link_status[(0, 2)] = link_status[(2, 0)] = True
    link_status[(1, 2)] = link_status[(2, 1)] = True
    link_status[(1, 3)] = link_status[(3, 1)] = True
    link_status[(2, 3)] = link_status[(3, 2)] = True

    # No loops
    for i in range(-1, n):
        link_status[(i, i)] = False

    # Links to DC
    # All valid (exist)
    for i in range(0, n):
        link_valid[(i, -1)] = link_valid[(-1, i)] = True

    # Links between SMs
    for i in range(0, n):
        for j in range(i + 1, n):
            link_valid[(i, j)] = link_valid[(j, i)] = False
    # All failed but five
    link_valid[(0, 1)] = link_valid[(1, 0)] = True
    link_valid[(0, 2)] = link_valid[(2, 0)] = True
    link_valid[(1, 2)] = link_valid[(2, 1)] = True
    link_valid[(1, 3)] = link_valid[(3, 1)] = True
    link_valid[(2, 3)] = link_valid[(3, 2)] = True

    # No loops exist
    for i in range(-1, n):
        link_valid[(i, i)] = False

    return sm_status, link_status, link_valid
