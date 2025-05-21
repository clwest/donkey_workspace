#!/bin/bash
set -e

# Simple wrapper to seed everything in one go
# Runs standard seeders and devdoc scripts sequentially

SCRIPT_DIR="$(dirname "$0")"

echo "🌱 Running full seeder pipeline..."

bash "$SCRIPT_DIR/run_all_seeders.sh"
bash "$SCRIPT_DIR/run_all_devdoc_scripts.sh"

echo "🎉 Full seeding complete!"
