# AggFT Implementation

## TODOs

- Complete installation section to the README.
- Add compression/decompression section to README.

## Installation

1. Install the [Nix Package Manager][nix-home].
2. Enable [Flakes][flake-wiki].
3. TODO

## Usage

You can use and extend the core AggFT implementation that is provided as a
Python package. Or you can use the companion simulation package to run
simulations.

### Simulations

There are three steps to run a simulation with `aggft-sim`:

1. Write simulation spec.
2. Run simulation.
3. Analyze results.

Documentation for the spec format is available at [docs/spec.md](docs/spec.md).
And documentation for the output format is available at
[docs/output.md](docs/output.md).

There is a special simulation command to run simulations based on the topology
of `Figure 1` in the paper. The command is `aggft-sim-fig`. Documentation for
its spec format is available at [docs/fig-spec.md](docs/fig-spec.md). It has the
same output format as `aggft-sim`.

#### Simulations Determinism

The simulations are not deterministic. There are three reasons for that.

The first reason is that cryptographic keys are not seeded. This means that
simulations using the same spec will have different cryptographic keys. While
this should not effect the simulation results, it should be noted.

The second reason is the use of multi-threading and multi-processing. Thread or
process scheduling can have an effect on the results.

The third reason is the use of time. This AggFT implementation relies heavily on
time. Running the simulations on a slow machine could cause more timeouts and
change the results.

However, the first and second reason should not greatly impact the results. To
tackle the third reason, the simulation package reports any issues with timouts
in the generated results. If you have such issues, you can run smaller-scale
simulations, or relax the time limits.

[nix-home]: https://nixos.org/
[flake-wiki]: https://nixos.wiki/wiki/Flakes
