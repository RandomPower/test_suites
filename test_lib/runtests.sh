#!/bin/bash
set -euo pipefail

# The tests never use a graphical display. When they are started from an SSH session with X11 forwarding
# (e.g. MobaXterm), the programs would inherit its DISPLAY: IID_validation would then draw its plots with
# matplotlib through the X server of the client, and would be killed ("X connection to localhost:10.0
# broken") if the session is closed while the tests run. Remove the display and use the non-interactive
# matplotlib backend, so the session can be closed at any time.
unset DISPLAY WAYLAND_DISPLAY
export MPLBACKEND=Agg

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

# End of the tests, shown in the Info sheet of the report
echo "$(timestamp) - Tests finished" >> "$OUTPUT_DIR"/runtests.log
/usr/local/bin/test_lib/report_generator >> "$OUTPUT_DIR"/runtests.log 2>&1
rm -f ._*.bin

echo "$(timestamp) - All tasks completed. Exit status: $status" >> "$OUTPUT_DIR"/runtests.log

exit "$status"