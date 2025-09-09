#!/bin/bash

PY_VENV_DIR="/usr/local/bin/test_lib/IID_validation/.venv/bin/python3"
MAIN_DIR="/usr/local/bin/test_lib/IID_validation/main.py"
CUR_DIR=$(pwd)

if [ -d binaries ]; then
    FILES=$(ls -1 "$CUR_DIR"/binaries/*.bin)
elif [ -d bins ]; then
    FILES=$(ls -1 "$CUR_DIR"/bins/*.bin)
else
    echo "No binaries directory found. Please create a directory named 'binaries' and place your .bin files in it."
    exit 1
fi


count = 0
for i in $FILES 
do
    nohup $PY_VENV_DIR $MAIN_DIR -i "$i" --no-stat_analysis &

    # Launch up to 5 processes at the time, then wait for their completion
    count=$((count + 1))
    if (( count % 5 == 0 )); then
        wait
    fi
done

wait