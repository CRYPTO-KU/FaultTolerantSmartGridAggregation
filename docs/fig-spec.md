# `aggft-sim-fig` Spec Format

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

## `n-min`

- Required.
- Type: Integer between `2` and `4`, inclusive.
- Description: Minimum number of smart meters to participate in the round.
- Example: `"n-min": 2`.

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

## `round-len`

- Required.
- Type: Float larger than or equal to `2`.
- Description: The allowed time (in seconds) for a round. Rounds taking longer
  time will terminate.
- Example: `"round-len": 2`.

## `phase-1-len`

- Required.
- Type: Float larger than or equal to `1`. Must be strictly less than
  `round-len`.
- Description: The allowed time (in seconds) for `phase-1`. Phases taking longer
  time will terminate.
- Example: `"phase-1-len": 1`.
