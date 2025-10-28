#!/bin/bash

pids=()
/usr/local/bin/test_lib/run_iid.sh & pids+=($!)
/usr/local/bin/test_lib/nist/run_nist_tests.sh & pids+=($!)
/usr/local/bin/test_lib/testu01 & pids+=($!)

for pid in "${pids[@]}"; do
    wait "$pid"
done

/usr/local/bin/test_lib/report_generator

rm -f ._*.bin
