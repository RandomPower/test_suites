#!/bin/bash
set -euo pipefail

CUR_DIR=$(pwd)
OUTPUT_DIR="$CUR_DIR/output_logs"
mkdir -p "$OUTPUT_DIR"

timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

echo "$(timestamp) - Starting runtests.sh" >> "$OUTPUT_DIR"/runtests.log

pids=()
/usr/local/bin/test_lib/run_iid.sh > "$OUTPUT_DIR"/iid.log 2>&1 &   pids+=($!)
/usr/local/bin/test_lib/nist/run_nist_tests.sh > "$OUTPUT_DIR"/nist.log 2>&1 &   pids+=($!)
/usr/local/bin/test_lib/testu01 > "$OUTPUT_DIR"/testu01.log 2>&1 &  pids+=($!)

set +e
status=0
for pid in "${pids[@]}"; do
    if wait "$pid"; then
        echo "Process $pid finished successfully" >> "$OUTPUT_DIR"/runtests.log
    else
        exit_code=$?
        echo "Process $pid exited with error code $exit_code" >> "$OUTPUT_DIR"/runtests.log
        status=1
    fi
done
set -e

/usr/local/bin/test_lib/report_generator >> "$OUTPUT_DIR"/runtests.log 2>&1
rm -f ._*.bin

echo "$(timestamp) - All tasks completed. Exit status: $status" >> "$OUTPUT_DIR"/runtests.log

exit "$status"