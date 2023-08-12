import argparse, json, random

from itertools import product

import aggft

from .report import report
from .validate import validate_spec
from .sim_one import simulate_one_mask, simulate_one_homomorphic
from .utils import generate_link_status, generate_sm_status


def main():
    args = parse_args()
    spec = get_spec(args)

    validate_spec(spec)

    random.seed(spec["random-seed"])

    simulate(spec)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run AggFT simulations from specification."
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

    startup_wait = spec["startup-wait"]
    round_len_constant = spec["round-len-constant"]
    phase_1_len_constant = spec["phase-1-len-constant"]

    zip_failure_probs = spec["zip-failure-probabilities"]
    dc_link_fail_probs = spec["dc-link-failure-probabilities"]
    sm_link_fail_probs = spec["sm-link-failure-probabilities"]
    sm_full_fail_probs = spec["sm-full-failure-probabilities"]
    dc_link_fail_exact = spec["dc-link-failure-exact"]
    sm_link_fail_exact = spec["sm-link-failure-exact"]
    sm_full_fail_exact = spec["sm-full-failure-exact"]

    props = product(
        spec["sm-counts"],
        spec["n-min-constants"],
        spec["privacy-types"],
    )

    for n, n_min_const, privacy_type in props:
        if spec["all-failure-possibilities"]:
            configs = all_configurations(n)
        else:
            configs = some_configurations(
                n,
                zip_failure_probs,
                dc_link_fail_probs,
                sm_link_fail_probs,
                sm_full_fail_probs,
                dc_link_fail_exact,
                sm_link_fail_exact,
                sm_full_fail_exact
            )
        for link_status, sm_status, *failure_probs in configs:
            n_min = int(max(2, n_min_const * n))
            dc_link_fail_p, sm_link_fail_p, sm_full_fail_p = failure_probs
            round_len = max(2.0, round_len_constant * n)
            phase_1_len = max(1.0, phase_1_len_constant * n)
            dc_link_fail_p, sm_link_fail_p, sm_full_fail_p = failure_probs

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
                    )

                report(
                    n,
                    n_min_const,
                    n_min,
                    privacy_type,
                    dc_link_fail_p,
                    sm_link_fail_p,
                    sm_full_fail_p,
                    dc_link_fail_exact,
                    sm_link_fail_exact,
                    sm_full_fail_exact,
                    link_status,
                    sm_status,
                    dc_report,
                    sm_reports,
                )

def some_configurations(
    n,
    zip_failure_probs,
    dc_link_fail_probs,
    sm_link_fail_probs,
    sm_full_fail_probs,
    dc_link_fail_exact,
    sm_link_fail_exact,
    sm_full_fail_exact
):
    if zip_failure_probs:
        all_failure_probs = list(zip(
            dc_link_fail_probs,
            sm_link_fail_probs,
            sm_full_fail_probs
        ))
    else:
        all_failure_probs = list(product(
            dc_link_fail_probs,
            sm_link_fail_probs,
            sm_full_fail_probs
        ))

    for dc_link_fail_p, sm_link_fail_p, sm_full_fail_p in all_failure_probs:
        link_status = generate_link_status(
            n, dc_link_fail_p, sm_link_fail_p, dc_link_fail_exact, sm_link_fail_exact
        )
        sm_status = generate_sm_status(n, sm_full_fail_p, sm_full_fail_exact)
        yield link_status, sm_status, dc_link_fail_p, sm_link_fail_p, sm_full_fail_p

def all_configurations(n):
    sm_status = [True] * n
    all_link_status = product(*([[0, 1]] * ((n + 1) * n // 2)))
    for s in all_link_status:
        link_status = {}
        link_idx = 0
        for i in range(0, n):
            link_status[(i, -1)] = link_status[(-1, i)] = s[link_idx]
            link_idx += 1
        for i in range(0, n):
            for j in range(i + 1, n):
                link_status[(i, j)] = link_status[(j, i)] = s[link_idx]
                link_idx += 1
        for i in range(-1, n):
            link_status[(i, i)] = False
        yield link_status, sm_status, "N/A", "N/A", "N/A"
