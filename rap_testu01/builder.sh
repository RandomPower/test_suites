#!/bin/bash
# Builds the rap_testu01 executable in ./build/src/rap_testu01.
# TestU01 itself is downloaded and built by CMake (see CMakeLists.txt):
# requires git, make, cmake >= 3.22 and access to github.com.
set -euo pipefail
cd "$(dirname "$0")"

cmake -S . -B build
cmake --build build -j"$(nproc)"
