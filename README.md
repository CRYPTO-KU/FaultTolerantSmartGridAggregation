# AggFT Implementation

## TODOs

- Support simulations with all link combinations.
- Support simulations with handcrafted link status (figure 3 from the paper).
- Add simulations with standard cryptographic key lengths (now we use short
  keys).
- Add installation section to the README.
- Benchmark basic computational operations (formulas in paper).

## Usage

You can use and extend the core AggFT implementation that is provided as a
Python package. Or you can use the companion simulation package to run
simulations.

### Simulations

There are four steps to run a simulation:

1. Decide simulation type (TODO: Mention types).
2. Write simulation spec.
3. Run simulation.
4. Analyze results.

Documentation for the spec files is available at [docs/spec](docs/spec). And
documentation for the result files is available at
[docs/csv-head](docs/csv-head).

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
