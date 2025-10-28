#!/bin/bash

NIST_ASSESS_DIR="/usr/local/bin/test_lib/nist/"
CUR_DIR=$(pwd)

export OMP_NUM_THREADS=32

create_dir_script() {
    if [ -z "${NISTFOLDER+x}" ]; then
        echo "NISTFOLDER is unset"
        return 0
    fi

    echo "Preparing NIST folder: $NISTFOLDER"
    mkdir -p "nist_results/$NISTFOLDER/AlgorithmTesting"/{Frequency,BlockFrequency,Runs,LongestRun,Rank,FFT,NonOverlappingTemplate,OverlappingTemplate,Universal,LinearComplexity,Serial,ApproximateEntropy,CumulativeSums,RandomExcursions,RandomExcursionsVariant}
}

if [ -d binaries ]; then
    FILES=$(ls -1 "$CUR_DIR"/binaries/*.bin)
elif [ -d bins ]; then
    FILES=$(ls -1 "$CUR_DIR"/bins/*.bin)
else
    echo "No binaries directory found. Please create a directory named 'binaries' and place your .bin files in it."
    exit 1
fi

if [ ! -d ./templates ]; then
    rsync -avz "$NIST_ASSESS_DIR/templates" .
fi

count=0
MAX_JOBS=20

for i in $FILES 
do
    export NISTFOLDER="$(basename "${i%.bin}")"
    create_dir_script
    "$NIST_ASSESS_DIR/assess" 1000000 -i "$i" -f 1 -n 2000 &

    # Launch up to 20 processes at the time, then wait for their completion
    ((count++))
    if (( count % MAX_JOBS == 0 )); then
        wait
    fi
done

wait

rm -rf ./templates