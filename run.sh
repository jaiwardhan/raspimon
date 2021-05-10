#!/bin/bash

# Raspimon monitor hook. Requires python3

PWD_TRIGGER=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/raspimon.py"
cd "$PWD_TRIGGER"
