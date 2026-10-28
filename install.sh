#!/bin/bash
# Builds the NIST STS, the TestU01 runner and the report generator and installs
# them, together with the IID validation procedure, in /usr/local/bin/test_lib.
# Admin rights (sudo) are needed to copy the files into /usr/local/bin.
set -euo pipefail
cd "$(dirname "$0")"

INSTALL_DIR=/usr/local/bin/test_lib

# IID_validation needs Python >= 3.11: check it now rather than after the long builds.
# If python3 is older, choose another interpreter with: PYTHON=python3.11 ./install.sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 11))' || {
    echo "Error: IID_validation needs Python >= 3.11, found $("$PYTHON" --version 2>&1)." >&2
    echo "Install it (e.g. sudo apt install python3.11 python3.11-venv) and run: PYTHON=python3.11 ./install.sh" >&2
    exit 1
}

# External repositories pinned as git submodules (IID_validation). sync applies URL changes
# made in .gitmodules to an existing clone.
git submodule sync --recursive
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

# Versions of the installed software, shown in the Info sheet of the reports
{
    echo "test_suites=$(git describe --tags --match "v[0-9]*" --always --dirty)"
    echo "IID_validation=$(git -C external/IID_validation describe --tags --match "v[0-9]*" --always --dirty)"
    echo "NIST_STS=2.1.2 with RaP changes (tag nist-sts-2.1.2)"
    echo "TestU01=1.2.3 (umontreal-simul/TestU01-2009 @ $(sed -n 's/.*GIT_TAG *\([0-9a-f]\{7\}\).*/\1/p' rap_testu01/CMakeLists.txt))"
} > test_lib/VERSION

# Give run permissions to the scripts
chmod +x test_lib/runtests.sh test_lib/run_iid.sh test_lib/raptests

# rsync -a run with sudo keeps the owner of test_lib (the current user),
# so the steps below do not need sudo
sudo rsync -avz test_lib /usr/local/bin/.

# 'raptests' command, available from any folder
sudo ln -sf "$INSTALL_DIR/raptests" /usr/local/bin/raptests

# Install the IID procedure, at the version pinned by the external/IID_validation submodule, with its own
# installer: virtual environment in IID_validation/.venv and compiled Rust core (if Rust is not installed,
# the build downloads a temporary toolchain). rust/target is kept to speed up the next builds.
rsync -a --delete --exclude .git --exclude .venv --exclude /rust/target/ \
    external/IID_validation/ "$INSTALL_DIR/IID_validation/"
"$INSTALL_DIR/IID_validation/install.sh"
