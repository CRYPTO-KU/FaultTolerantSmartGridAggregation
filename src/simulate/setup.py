#!/usr/bin/env python

from distutils.core import setup

setup(
    name="AggFT Simulate",
    version="0.1.0",
    description="Run simulations using the AggFT implementation.",
    author="Ameer Taweel",
    packages=["simulate"],
    entry_points={
        "console_scripts": [
            "aggft-sim=simulate.sim_parallel:main",
        ],
    },
)
