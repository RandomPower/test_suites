#!/bin/bash
set -euo pipefail

PY_VENV_DIR="/usr/local/bin/test_lib/IID_validation/.venv/bin/python3"
MAIN_DIR="/usr/local/bin/test_lib/IID_validation/main.py"
CUR_DIR=$(pwd)
OUTPUT_DIR="$CUR_DIR/output_logs"
mkdir -p "$OUTPUT_DIR"

if [ -d binaries ]; then
    FILES=("$CUR_DIR"/binaries/*.bin)
elif [ -d bins ]; then
    FILES=("$CUR_DIR"/bins/*.bin)
else
    echo "No binaries directory found."
    exit 1
fi

MAX_JOBS=5
for i in "${FILES[@]}"; do
    filename=$(basename "$i")
    "$PY_VENV_DIR" "$MAIN_DIR" -i "$i" --no-stat_analysis > "$OUTPUT_DIR/${filename%.bin}.log" 2>&1 &
    while (( $(jobs -r | wc -l) >= MAX_JOBS )); do
        wait -n
    done
done
wait