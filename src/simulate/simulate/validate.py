import sys


def validate_spec(spec):
    key = "simulations-per-config"
    require(spec, key)
    require_int_leq(spec, key, 1)

    key = "processes"
    require(spec, key)
    require_int_leq(spec, key, 1)

    key = "random-seed"
    require(spec, key)
    require_int_leq(spec, key, 0)

    key = "sm-counts"
    require(spec, key)
    require_list_of_int_leq(spec, key, 2)

    key = "n-min-constants"
    require(spec, key)
    require_list_of_probability(spec, key)

    key = "all-failure-possibilities"
    require(spec, key)
    require_bool(spec, key)

    if not spec[key]:
        key = "zip-failure-probabilities"
        require(spec, key)
        require_bool(spec, key)

        key = "dc-link-failure-probabilities"
        require(spec, key)
        require_list_of_probability(spec, key)

        key = "dc-link-failure-exact"
        require(spec, key)
        require_bool(spec, key)

        key = "sm-link-failure-probabilities"
        require(spec, key)
        require_list_of_probability(spec, key)

        key = "sm-link-failure-exact"
        require(spec, key)
        require_bool(spec, key)

        key = "sm-full-failure-probabilities"
        require(spec, key)
        require_list_of_probability(spec, key)

        key = "sm-full-failure-exact"
        require(spec, key)
        require_bool(spec, key)

    key = "privacy-types"
    require(spec, key)
    require_list_of_enum(spec, key, ["mask", "encr"])

    key = "masking-modulus"
    if "mask" in spec["privacy-types"]:
        require(spec, key)
        require_int_leq(spec, key, 2)

    key = "prf-key-len"
    if "mask" in spec["privacy-types"]:
        require(spec, key)
        require_int_leq(spec, key, 1)

    key = "homomorphic-key-len"
    if "encr" in spec["privacy-types"]:
        require(spec, key)
        require_int_leq(spec, key, 1)

    key = "startup-wait"
    require(spec, key)
    require_float_l(spec, key, 0)

    key = "round-len-constant"
    require(spec, key)
    require_float_l(spec, key, 0)

    cmp = key
    key = "phase-1-len-constant"
    require(spec, key)
    require_float_l(spec, key, 0)
    if spec[key] >= spec[cmp]:
        sys.exit(f"ERROR: {key} should be strictly less than {cmp}.")


def validate_fig_spec(spec):
    key = "simulations-per-config"
    require(spec, key)
    require_int_leq(spec, key, 1)

    key = "processes"
    require(spec, key)
    require_int_leq(spec, key, 1)

    key = "random-seed"
    require(spec, key)
    require_int_leq(spec, key, 0)

    key = "n-min"
    require(spec, key)
    require_int_range(spec, key, 2, 4)

    key = "privacy-types"
    require(spec, key)
    require_list_of_enum(spec, key, ["mask", "encr"])

    key = "masking-modulus"
    if "mask" in spec["privacy-types"]:
        require(spec, key)
        require_int_leq(spec, key, 2)

    key = "prf-key-len"
    if "mask" in spec["privacy-types"]:
        require(spec, key)
        require_int_leq(spec, key, 1)

    key = "homomorphic-key-len"
    if "encr" in spec["privacy-types"]:
        require(spec, key)
        require_int_leq(spec, key, 1)

    key = "startup-wait"
    require(spec, key)
    require_float_l(spec, key, 0)

    key = "round-len"
    require(spec, key)
    require_float_leq(spec, key, 2)

    cmp = key
    key = "phase-1-len"
    require(spec, key)
    require_float_leq(spec, key, 1)
    if spec[key] >= spec[cmp]:
        sys.exit(f"ERROR: {key} should be strictly less than {cmp}.")


################################################################################
# Primitive Type Helpers
################################################################################


def is_int(x):
    return isinstance(x, int) or (isinstance(x, float) and int(x) == x)


def is_float(x):
    return isinstance(x, float) or isinstance(x, int)


def is_bool(x):
    return isinstance(x, bool)


def is_str(x):
    return isinstance(x, str)


def is_list(x):
    return isinstance(x, list)


################################################################################
# Validation Helpers
################################################################################


# Require a key to be defined in the spec
def require(spec, key):
    if key not in spec:
        sys.exit(f"ERROR: {key} not found in spec.")


# Require value to be a boolean
def require_bool(spec, key):
    if not is_bool(spec[key]):
        sys.exit(f"ERROR: {key} is not a boolean.")


# Require value to be an integer and larger than or equal to x
def require_int_leq(spec, key, x):
    if not is_int(spec[key]):
        sys.exit(f"ERROR: {key} is not an integer.")
    if spec[key] < x:
        sys.exit(f"ERROR: {key} should be larger than or equal to {x}.")
    spec[key] = int(spec[key])


# Require value to be an integer in the range [x, y]
def require_int_range(spec, key, x, y):
    if not is_int(spec[key]):
        sys.exit(f"ERROR: {key} is not an integer.")
    if spec[key] < x or spec[key] > y:
        sys.exit(f"ERROR: {key} should be in [{x}, {y}].")
    spec[key] = int(spec[key])


def require_float_l(spec, key, x):
    if not is_float(spec[key]):
        sys.exit(f"ERROR: {key} is not a float.")
    if spec[key] <= x:
        sys.exit(f"ERROR: {key} should be strictly larger than {x}.")
    spec[key] = float(spec[key])


def require_float_leq(spec, key, x):
    if not is_float(spec[key]):
        sys.exit(f"ERROR: {key} is not a float.")
    if spec[key] < x:
        sys.exit(f"ERROR: {key} should be larger or equal to {x}.")
    spec[key] = float(spec[key])


# Require value to be a list of integers larger than or equal to x
def require_list_of_int_leq(spec, key, x):
    if not is_list(spec[key]):
        sys.exit(f"ERROR: {key} is not a list.")
    for i, n in enumerate(spec[key]):
        if not is_int(n):
            sys.exit(f"ERROR: {key} has non-integer values.")
        if n < x:
            sys.exit(
                f"ERROR: {key} should have all values " f"larger than or equal to {x}."
            )
        spec[key][i] = int(spec[key][i])


# Require value to be a list of floats between 0 and 1, inclusive
def require_list_of_probability(spec, key):
    if not is_list(spec[key]):
        sys.exit(f"ERROR: {key} is not a list.")
    for i, n in enumerate(spec[key]):
        if not is_float(n):
            sys.exit(f"ERROR: {key} has non-float values.")
        if n < 0 or n > 1:
            sys.exit(
                f"ERROR: {key} should have all values " f"between 0 and 1, inclusive."
            )
        spec[key][i] = float(spec[key][i])


# Require value to be a list of strings with finite allowed values
def require_list_of_enum(spec, key, values):
    if not is_list(spec[key]):
        sys.exit(f"ERROR: {key} is not a list.")
    for n in spec[key]:
        if not is_str(n):
            sys.exit(f"ERROR: {key} has non-string values.")
        if n not in values:
            sys.exit(f"ERROR: {key} should have all values in {values}.")
