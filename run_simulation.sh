#!/bin/bash
# Convenience script to run the Historical Mind-Lab simulation

cd "$(dirname "$0")"
PYTHONPATH=$(pwd) python3 src/main_cli.py "$@"
