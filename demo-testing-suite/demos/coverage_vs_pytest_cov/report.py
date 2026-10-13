"""A small command-line tool -- not a test. pytest never runs it.

Usage:  python report.py -5 30
"""
import sys

from tempconv.temps import describe, to_fahrenheit

for arg in sys.argv[1:]:
    c = float(arg)
    f = to_fahrenheit(c)
    print(f"{c} C = {f} F ({describe(c)})")
