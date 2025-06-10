#!/bin/bash
set -e
SCRIPT_DIR="$(dirname "$0")/.."
cd "$SCRIPT_DIR/backend"
./seed_all.sh
