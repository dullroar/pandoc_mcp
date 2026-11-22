#!/usr/bin/env python3
"""Compatibility entry point. Usage: build_context_indexes.py [--check] [ROOT]

Run me when: using an existing command that rebuilds or checks the context indexes.
"""
import sys

from build_indexes import main


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
