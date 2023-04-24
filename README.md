# Proven Smart Grid Security (AggFT)

To run the failure check code:

```bash
mkdir -p results
./aggft/failure_check.py > results/failure_check.csv
```

To run the performance check code:

```bash
mkdir -p results
./aggft/parallel_performance_check.rb 1008 24 > results/performance_check.csv
```
