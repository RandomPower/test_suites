#!/bin/bash
# Builds the NIST STS, the TestU01 runner and the report generator and installs
# them, together with the IID validation procedure, in /usr/local/bin/test_lib.
# Admin rights (sudo) are needed to copy the files into /usr/local/bin.
set -euo pipefail
cd "$(dirname "$0")"

INSTALL_DIR=/usr/local/bin/test_lib

# External repositories pinned as git submodules (IID_validation)
git submodule update --init --recursive

# Compile the nist test suite
make -C nist_tests
chmod +x nist_tests/assess nist_tests/run_nist_tests.sh

# Copy the files in final executable folder
mkdir -p test_lib/nist
cp nist_tests/assess nist_tests/run_nist_tests.sh test_lib/nist/
rsync -a nist_tests/templates test_lib/nist/

# Compile the TestU01 library and test runner (TestU01 is downloaded and built by CMake)
rap_testu01/builder.sh

# Set environment and create report generator
(cd report_generator && chmod +x build.sh && ./build.sh)
cp report_generator/dist/report_generator test_lib/

# Copy the TestU01 runner in the new folder
cp rap_testu01/build/src/rap_testu01 test_lib/testu01

# Give run permissions to the scripts
chmod +x test_lib/runtests.sh test_lib/run_iid.sh test_lib/raptests

# rsync -a run with sudo keeps the owner of test_lib (the current user),
# so the steps below do not need sudo
sudo rsync -avz test_lib /usr/local/bin/.

# 'raptests' command, available from any folder
sudo ln -sf "$INSTALL_DIR/raptests" /usr/local/bin/raptests

# Install the IID procedure, at the version pinned by the external/IID_validation submodule
rsync -a --delete --exclude .git --exclude .venv external/IID_validation/ "$INSTALL_DIR/IID_validation/"
cd "$INSTALL_DIR/IID_validation"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install .
