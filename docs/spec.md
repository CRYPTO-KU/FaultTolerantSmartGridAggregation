# `aggft-sim` Spec Format

The simulation spec should be in the JSON format. This document describes all
the possible fields in the spec file.

## `simulations-per-config`

- Required.
- Type: Integer larger than or equal to `1`.
- Description: Specifies the number of simulation to run per configuration. If
  using multiple processes, each process will run `simulations-per-config`
  simulations per configuration. Therefore, each configuration will be run
  `simulations-per-config * processes` many times.
- Example: `"simulations-per-config": 5`.

## `processes`

- Required.
- Type: Integer larger than or equal to `1`.
- Description: Specifies the number of processes to use to run the simulations.
  If using multiple processes, each process will run `simulations-per-config`
  simulations per configuration. Therefore, each configuration will be run
  `simulations-per-config * processes` many times.
- Example: `"processes": 12`.

## `random-seed`

- Required.
- Type: Integer larger than or equal to `0`.
- Description: Specifies the seed for randomness in the generator. However,
  cryptographic keys are not seeded.
- Example: `"random-seed": 0`.

## `sm-counts`

- Required.
- Type: A list of integers larger than or equal to `2`.
- Description: Specifies the number of smart meters in a simulation.
- Example: `"sm-counts": [50, 100, 200, 400]`.

## `n-min-constants`

- Required.
- Type: List of floats between `0` and `1`, inclusive.
- Description: `n-min` will be computed by `int(max(2, n-min-constant * n))`.
- Example: `"n-min-constants": [0.25, 0.5, 0.75]`.

## `all-failure-possibilities`

- Required.
- Type: Boolean.
- Description: When `true`, will simulate all combinations of link failures.
  Otherwise, will simulate a subset of those combinations based on the failure
  probabilities provided in other fields. Don't set to `ture` for large numbers
  of smart meters, because the number of combinations blows up.
- Example: `"all-failure-possibilities": false`.

## `zip-failure-probabilities`

- Required if `all-failure-possibilities` is `false`.
- Type: Boolean.
- Description: Whether or not to zip failure probabilities. For example, assume
  DC link failure probabilities are `[0.1, 0.2]`, SM link failure probabilities
  are `[0.3, 0.4]`, and SM full failure probabilities are `[0.5, 0.6]`. When
  `zip-failure-probabilities` is `true`, we will have the following failure
  probabilities: `[(0.1, 0.3, 0.5), (0.2, 0.4, 0.6)]`. Otherwise, we will have
  `[(0.1, 0.3, 0.5), (0.1, 0.3, 0.6), (0.1, 0.4, 0.5), (0.1, 0.4, 0.6),
  (0.2, 0.3, 0.5), (0.2, 0.3, 0.6), (0.2, 0.4, 0.5), (0.2, 0.4, 0.6)]`.
- Example: `"zip-failure-probabilities": true`.

## `dc-link-failure-probabilities`

- Required if `all-failure-possibilities` is `false`.
- Type: A list of probabilities (floats between `0` and `1`, inclusive).
- Description: Specifies the failure probability for links between a DC and an
  SM.
- Example: `"dc-link-failure-probabilities": [0, 0.1, 0.2, 0.4]`.

## `dc-link-failure-exact`

- Required if `all-failure-possibilities` is `false`.
- Type: Boolean.
- Description: Whether or not to force exact failure probability. Setting this
  to `true` will force the failed links to be exactly equal to the float in
  `dc-link-failure-probabilities`. Setting this to `false` will toss a coin for
  each link with the specified failure probability.
- Example: `"dc-link-failure-exact": true`.

## `sm-link-failure-probabilities`

- Required if `all-failure-possibilities` is `false`.
- Type: A list of probabilities (floats between `0` and `1`, inclusive).
- Description: Specifies the failure probability for links between an SM and
  another SM.
- Example: `"sm-link-failure-probabilities": [0, 0.1, 0.2, 0.4]`.

## `sm-link-failure-exact`

- Required if `all-failure-possibilities` is `false`.
- Type: Boolean.
- Description: Whether or not to force exact failure probability. Setting this
  to `true` will force the failed links to be exactly equal to the float in
  `sm-link-failure-probabilities`. Setting this to `false` will toss a coin for
  each link with the specified failure probability.
- Example: `"sm-link-failure-exact": true`.

## `sm-full-failure-probabilities`

- Required if `all-failure-possibilities` is `false`.
- Type: A list of probabilities (floats between `0` and `1`, inclusive).
- Description: Specifies the failure probability for smart meters.
- Example: `"sm-full-failure-probabilities": [0, 0.1, 0.2, 0.4]`.

## `sm-full-failure-exact`

- Required if `all-failure-possibilities` is `false`.
- Type: Boolean.
- Description: Whether or not to force exact failure probability. Setting this
  to `true` will force the failed SMs to be exactly equal to the float in
  `sm-full-failure-probabilities`. Setting this to `false` will toss a coin for
  each SM with the specified failure probability.
- Example: `"sm-full-failure-exact": true`.

## `privacy-types`

- Required.
- Type: List of strings (possible values: `mask` and `encr`).
- Description: `mask` enables the use of masking by AggFT. While `encr` enables
  the use of homomorphic encryption.
- Example: `"privacy-types": ["mask", "encr"]`.

## `masking-modulus`

- Required if `privacy-types` contains `mask`.
- Type: Integer larger than or equal to `2`.
- Description: Used as the modules `k` in masking mode (refer to the paper).
- Example: `"masking-modulus": 2e20`.

## `prf-key-len`

- Required if `privacy-types` contains `mask`.
- Type: Integer larger than or equal to `1`.
- Description: The legnth (in bytes) of the PRF key. Note that cryptographic
  keys are not seeded using `random-seed`.
- Example: `"prf-key-len": 32`.

## `homomorphic-key-len`

- Required if `privacy-types` contains `encr`.
- Type: Integer larger than or equal to `1`.
- Description: The legnth (in bytes) of the homomorphic encryption keys. Note
  that cryptographic keys are not seeded using `random-seed`.
- Example: `"homomorphic-key-len": 256`.

## `startup-wait`

- Required.
- Type: Float larger than `0`.
- Description: The time (in seconds) to wait before executing the simulation.
  Setting this to a reasonable amount is important. Otherwise, threads might try
  to contact each others before all threads are ready.
- Example: `"startup-wait": 0.1`.

## `round-len-constant`

- Required.
- Type: Float larger than `0`.
- Description: The allowed time (in seconds) for a round. Rounds taking longer
  time will terminate. The time will be computed as `round-len-constant * n`.
  Times less than `2` seconds will be counted as `2` seconds.
- Example: `"round-len-constant": 0.1`.

## `phase-1-len-constant`

- Required.
- Type: Float larger than `0`. Must be strictly less than `round-len-constant`.
- Description: The allowed time (in seconds) for `phase-1`. Phases taking longer
  time will terminate. The time will be computed as `phase-1-len-constant * n`.
  Times less than `1` second will be counted as `1` second.
- Example: `"phase-1-len-constant": 0.005`.
