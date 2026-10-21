#!/bin/bash
set -euo pipefail

NIST_ASSESS_DIR="${NIST_ASSESS_DIR:-/usr/local/bin/test_lib/nist}"
CUR_DIR=$(pwd)

create_dir_script() {
    mkdir -p "nist_results/$NISTFOLDER/AlgorithmTesting"/{Frequency,BlockFrequency,Runs,LongestRun,Rank,FFT,NonOverlappingTemplate,OverlappingTemplate,Universal,LinearComplexity,Serial,ApproximateEntropy,CumulativeSums,RandomExcursions,RandomExcursionsVariant}
}

shopt -s nullglob
if [ -d binaries ]; then
    FILES=( "$CUR_DIR"/binaries/*.bin )
elif [ -d bins ]; then
    FILES=( "$CUR_DIR"/bins/*.bin )
else
    echo "No binaries directory found."
    exit 1
fi
if [ ${#FILES[@]} -eq 0 ]; then
    echo "No .bin files found in the binaries directory."
    exit 1
fi

mkdir -p ./templates
rsync -a "$NIST_ASSESS_DIR/templates/" ./templates/ || true

# Parallelism: one assess per .bin file, at most one per core. When there are
# fewer files than cores, the spare cores go to OpenMP, which runs the 15 tests
# of each bitstream in parallel (more than 15 threads per file would stay idle).
# NIST_CORES overrides the number of cores to use.
CORES=${NIST_CORES:-$(nproc)}
NFILES=${#FILES[@]}
MAX_JOBS=$(( NFILES < CORES ? NFILES : CORES ))
THREADS=$(( CORES / MAX_JOBS ))
if [ "$THREADS" -gt 15 ]; then THREADS=15; fi
if [ "$THREADS" -lt 1 ]; then THREADS=1; fi
export OMP_NUM_THREADS=$THREADS
echo "NIST: $NFILES files, $MAX_JOBS in parallel, $OMP_NUM_THREADS OpenMP threads each"

for i in "${FILES[@]}"; do
    export NISTFOLDER="$(basename "${i%.bin}")"
    create_dir_script

    {
        # Run assess, fix its buggy exit code. "|| ec=$?" is needed because
        # set -e is inherited here and would exit before checking the code.
        ec=0
        "$NIST_ASSESS_DIR/assess" 1000000 -i "$i" -f 1 -n 2000 || ec=$?
        # Treat exit code 1 (wrongly used for success) as success
        if [ $ec -eq 1 ]; then
            exit 0
        else
            exit $ec
        fi
    } > "nist_results/${NISTFOLDER}/log.txt" 2>&1 &

    # Throttle to MAX_JOBS concurrent jobs
    while (( $(jobs -r | wc -l) >= MAX_JOBS )); do
        wait -n 2>/dev/null || true
    done
done

# Wait for all remaining jobs (without aborting)
set +e
status=0
for job in $(jobs -p); do
    if ! wait "$job"; then
        echo "Job $job exited with error code $?" >&2
        status=1
    fi
done
set -e

rm -rf ./templates

exit "$status"

