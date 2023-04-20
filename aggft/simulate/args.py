import argparse

################################################################################
# Parse Arguments
################################################################################

def parse_args():
    parser = argparse.ArgumentParser(description = "Run AggFT simulations.")

    parser.add_argument(
        "--privacy-type",
        dest = "PRIVACY_TYPE",
        required = True,
        type = str,
        choices = [ "mask", "encr" ],
        help = "Privacy method to use"
    )

    parser.add_argument(
        "--n",
        dest = "SM_COUNT",
        required = True,
        type = int,
        help = "Number of smart meters"
    )

    parser.add_argument(
        "--n-min",
        dest = "N_MIN",
        required = True,
        type = int,
        help = "Minimum number of smart meters in a round"
    )

    parser.add_argument(
        "--round-len",
        dest = "ROUND_LEN",
        required = False,
        type = float,
        default =  5.0,
        help = "Round length in seconds (default: 5.0)"
    )

    parser.add_argument(
        "--phase-1-len",
        dest = "PHASE_1_LEN",
        required = False,
        type = float,
        default =  2.0,
        help = "Phase 1 length in seconds (default: 2.0)"
    )

    parser.add_argument(
        "--startup-wait",
        dest = "STARTUP_WAIT",
        required = False,
        type = float,
        default =  0.1,
        help = "The wait before starting each round in seconds (default: 0.1)"
    )

    return parser.parse_args()
