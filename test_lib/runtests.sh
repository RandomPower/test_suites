#!/bin/bash

nohup /usr/local/bin/test_lib/nist/run_nist_tests.sh &
nohup /usr/local/bin/test_lib/testu01/rap_testu01 &

wait

/usr/local/bin/test_lib/report_generator

# Remove the automatically generated junk bin files
rm ._*.bin