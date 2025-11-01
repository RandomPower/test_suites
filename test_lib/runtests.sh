#!/bin/bash
set -euo pipefail

CUR_DIR=$(pwd)
OUTPUT_DIR="$CUR_DIR/output_logs"
mkdir -p "$OUTPUT_DIR"

pids=()
/usr/local/bin/test_lib/run_iid.sh > "$OUTPUT_DIR"/iid.log 2>&1 &   pids+=($!)
/usr/local/bin/test_lib/nist/run_nist_tests.sh > "$OUTPUT_DIR"/nist.log 2>&1 &   pids+=($!)
/usr/local/bin/test_lib/testu01 > "$OUTPUT_DIR"/testu01.log 2>&1 &  pids+=($!)

for pid in "${pids[@]}"; do
    wait "$pid"
done

/usr/local/bin/test_lib/report_generator >> "$OUTPUT_DIR"/runtests.log 2>&1
rm -f ._*.bin