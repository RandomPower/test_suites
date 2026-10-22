#!/bin/bash
# Checks that the NIST STS in this repository produces exactly the same output
# as the original NIST STS 2.1.2.
#
# It builds two versions from git:
#   original  nist_tests as distributed by NIST (tag nist-sts-2.1.2)
#   current   nist_tests in this working tree (RaP command line, OpenMP,
#             faster counting in Linear Complexity, Non-overlapping Template,
#             Serial and Approximate Entropy)
# runs both on the same file with all 15 tests and default parameters, and
# compares every output file byte by byte (stats.txt, results.txt, data*.txt,
# freq.txt, finalAnalysisReport.txt).
#
# Usage: nist_tests/verify_against_original.sh <file.bin> [num_bitstreams] [stream_length]
#   defaults: num_bitstreams = 10, stream_length = 1000000
#   ORIGINAL_REF=<git ref> overrides the reference version (default nist-sts-2.1.2)
set -euo pipefail

if [ $# -lt 1 ]; then
    sed -n '2,17p' "$0"; exit 2
fi
BIN=$(realpath "$1"); NSTREAMS=${2:-10}; LEN=${3:-1000000}
ORIGINAL_REF=${ORIGINAL_REF:-nist-sts-2.1.2}
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
TESTS="Frequency BlockFrequency Runs LongestRun Rank FFT NonOverlappingTemplate OverlappingTemplate Universal LinearComplexity Serial ApproximateEntropy CumulativeSums RandomExcursions RandomExcursionsVariant"

# ---- original NIST STS 2.1.2 (interactive) --------------------------------
mkdir -p "$WORK/original"
git -C "$REPO" archive "$ORIGINAL_REF" nist_tests | tar -x -C "$WORK/original"
O="$WORK/original/nist_tests"
sed -i 's/^GCCFLAGS = -c -Wall$/GCCFLAGS = -c -Wall -O2/' "$O/makefile"   # same optimization as ours
mkdir -p "$O/obj"
for t in $TESTS; do mkdir -p "$O/experiments/AlgorithmTesting/$t"; done
make -s -C "$O" > "$WORK/original_build.log" 2>&1
SECONDS=0
# answers: input file, file name, all tests, no parameter changes, number of streams, binary format
(cd "$O" && printf "0\n%s\n1\n0\n%s\n1\n" "$BIN" "$NSTREAMS" | ./assess "$LEN" > "$WORK/original_run.log" 2>&1) || true
echo "original NIST STS 2.1.2: ${SECONDS} s"

# ---- current version (this working tree) ----------------------------------
mkdir -p "$WORK/current"
(cd "$HERE" && tar -c --exclude=./obj --exclude=./assess .) | tar -x -C "$WORK/current"
C="$WORK/current"
make -s -C "$C" > "$WORK/current_build.log" 2>&1
for t in $TESTS; do mkdir -p "$C/nist_results/verify/AlgorithmTesting/$t"; done
SECONDS=0
(cd "$C" && NISTFOLDER=verify ./assess "$LEN" -i "$BIN" -f 1 -n "$NSTREAMS" > "$WORK/current_run.log" 2>&1) || true
echo "current version:         ${SECONDS} s (OMP_NUM_THREADS=${OMP_NUM_THREADS:-all cores})"

# ---- comparison ---------------------------------------------------------------
A="$O/experiments/AlgorithmTesting"
B="$C/nist_results/verify/AlgorithmTesting"
NFILES=$(find "$A" -name "*.txt" -size +0 | wc -l)
NPV=$(cat "$A"/*/results.txt | wc -l)
if [ "$NPV" -eq 0 ]; then
    echo "ERROR: the original produced no results (check the file and the number of bitstreams)"
    exit 2
fi
if diff -r "$A" "$B" > "$WORK/diff.txt"; then
    echo "OK: $NFILES output files ($NPV p-values) are byte-for-byte identical"
else
    echo "DIFFERENCES FOUND:"
    head -40 "$WORK/diff.txt"
    exit 1
fi
