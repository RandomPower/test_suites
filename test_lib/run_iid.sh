#!/bin/bash
set -euo pipefail

IID_DIR="${IID_DIR:-/usr/local/bin/test_lib/IID_validation}"
PY_VENV_DIR="$IID_DIR/.venv/bin/python3"
MAIN_DIR="$IID_DIR/main.py"
CUR_DIR=$(pwd)
OUTPUT_DIR="$CUR_DIR/output_logs"
mkdir -p "$OUTPUT_DIR"

shopt -s nullglob
if [ -d binaries ]; then
    FILES=("$CUR_DIR"/binaries/*.bin)
elif [ -d bins ]; then
    FILES=("$CUR_DIR"/bins/*.bin)
else
    echo "No binaries directory found."
    exit 1
fi
if [ ${#FILES[@]} -eq 0 ]; then
    echo "No .bin files found in the binaries directory."
    exit 1
fi

# Parallelism: up to IID_MAX_JOBS files at a time (default 5). The cores are split among them:
# each file runs its permutations on its share of threads (Rust backend, RAYON_NUM_THREADS).
# IID_CORES overrides the number of cores to use.
CORES=${IID_CORES:-$(nproc)}
MAX_JOBS=${IID_MAX_JOBS:-5}
NFILES=${#FILES[@]}
if [ "$NFILES" -lt "$MAX_JOBS" ]; then MAX_JOBS=$NFILES; fi
THREADS=$(( CORES / MAX_JOBS ))
if [ "$THREADS" -lt 1 ]; then THREADS=1; fi
export RAYON_NUM_THREADS=$THREADS
echo "IID: $NFILES files, $MAX_JOBS in parallel, $RAYON_NUM_THREADS threads each (Rust backend)"

# A failed file does not stop the others: its name is written to iid_failed.txt and
# the script exits with an error at the end
FAILED="$OUTPUT_DIR/iid_failed.txt"
rm -f "$FAILED"
for i in "${FILES[@]}"; do
    filename=$(basename "$i")
    sleep 1

    {
        "$PY_VENV_DIR" "$MAIN_DIR" -i "$i" --no-stat_analysis --backend rust \
            > "$OUTPUT_DIR/${filename%.bin}.log" 2>&1 || echo "$filename" >> "$FAILED"
    } &
    while (( $(jobs -r | wc -l) >= MAX_JOBS )); do
        wait -n || true
    done
done
wait

if [ -s "$FAILED" ]; then
    echo "IID failed for: $(tr '\n' ' ' < "$FAILED")(see the .log files in $OUTPUT_DIR)" >&2
    exit 1
fi
