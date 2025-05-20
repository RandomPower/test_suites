#!/bin/bash

NIST_ASSESS_DIR="/usr/local/bin/test_lib/nist/"
CUR_DIR=$(pwd)

export OMP_NUM_THREADS=32

create_dir_script() {
# Create Directory Structure

    if [ -z "${NISTFOLDER+x}" ]; then
        echo "NISTFOLDER is unset"
        exit 0
    else
        echo "NISTFOLDER is set to '$NISTFOLDER'"

        if [ ! -d nist_results ]; then
            echo "Directory 'nist_results' does not exist. Creating it."
            mkdir nist_results
        fi
        cd nist_results

        mkdir "$NISTFOLDER"
        cd "$NISTFOLDER"

        for diiname in AlgorithmTesting; do # BBS CCG G-SHA1 LCG MODEXP MS QCG1 QCG2 XOR
            mkdir "$diiname"
        done

        for dname in AlgorithmTesting; do # BBS CCG G-SHA1 LCG MODEXP MS QCG1 QCG2 XOR
            mkdir "$dname/Frequency"
            mkdir "$dname/BlockFrequency"
            mkdir "$dname/Runs"
            mkdir "$dname/LongestRun"
            mkdir "$dname/Rank"
            mkdir "$dname/FFT"
            mkdir "$dname/NonOverlappingTemplate"
            mkdir "$dname/OverlappingTemplate"
            mkdir "$dname/Universal"
            mkdir "$dname/LinearComplexity"
            mkdir "$dname/Serial"
            mkdir "$dname/ApproximateEntropy"
            mkdir "$dname/CumulativeSums"
            mkdir "$dname/RandomExcursions"
            mkdir "$dname/RandomExcursionsVariant"
        done
        cd ..
        cd ..
    fi
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
    rsync -avz $NIST_ASSESS_DIR/templates .
fi

count = 0
for i in $FILES 
do
    export NISTFOLDER="$(basename "${i%.bin}")"
    create_dir_script
    nohup $NIST_ASSESS_DIR/assess 1000000 -i "$i" -f 1 -n 2000 &

    # Launch up to 20 processes at the time, then wait for their completion
    count=$((count + 1))
    if (( count % 20 == 0 )); then
        wait
    fi
done

wait

rm -rf ./templates