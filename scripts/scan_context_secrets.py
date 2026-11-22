#!/usr/bin/env python3
"""Compatibility entry point. Usage: scan_context_secrets.py [ROOT]

Run me when: using an existing command that scans context for secrets.
"""
import sys

from scan_secrets import main


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
