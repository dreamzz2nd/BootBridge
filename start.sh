#!/usr/bin/env bash
# BootBridge Startup Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

python3 "$SCRIPT_DIR/bootbridge.py" "$@"
