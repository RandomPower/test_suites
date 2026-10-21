# NIST and TestU01 Libraries
Repo containing an automatic procedure to run the NIST test suite and TestU01 with creation of a final analysis Excel report

## Components and versions
- `nist_tests/`: NIST STS 2.1.2, imported unchanged in the commit tagged `nist-sts-2.1.2`, plus our changes
  (non-interactive command line, OpenMP, faster counting with byte-identical output). See `nist_tests/README.MD`.
- `rap_testu01/`: our TestU01 runner. TestU01 1.2.3 itself is downloaded by CMake at a fixed upstream commit.
- `external/IID_validation`: git submodule with the IID validation procedure (NIST SP 800-90B permutation tests),
  pinned to a fixed version.
- `report_generator/`: builds the final Excel report.

## Installation
Requirements: gcc, make, cmake >= 3.22, git, rsync, python3 with venv, and access to github.com
(TestU01 and the IID_validation submodule are downloaded during the installation).

Navigate with the terminal into the test_suites directory and run the following commands to automatically compile the NIST and TestU01 libraries and to move them in /usr/local/bin/
Admin powers will be required for this last operation.

```
chmod +x install.sh
./install.sh
```

The generated executables will be moved into /usr/local/bin/test_lib/ and will have the following structure:

```
/usr/local/bin/test_lib
    ├── nist/
    │   ├── assess
    │   ├── run_nist_tests.sh
    │   └── templates/
    ├── IID_validation/
    ├── testu01
    ├── report_generator
    ├── run_iid.sh
    └── runtests.sh
```

## Running the tests
Set the workspace to be the folder where you want the results to be generated.
There must be a folder called "binaries" or "bins" containing the binaries in the workspace.

To run the tests, run the following command from the workspace:

```
raptests
```
As the tests will take a lot of time, they are started in the background (with nohup) and keep running after
you log out. Progress is logged in `output_logs/` (`tail -f output_logs/runtests.log`) and the Excel report is
written to the workspace at the end. `raptests -f` runs the tests in the foreground instead, `raptests -h`
shows the help. Starting `raptests` again in a folder where the tests are still running is refused.

The structure of the folders, at the end of the tests, will be as follows:

```
main_worskpace/
    ├── binaries/ (or bins/)
    │   ├── binary1
    │   └── binary2
    ├── nist_results/
    │   └── $NISTFOLDER/
    │       ├── etc/
    │       └── etc2/
    ├── set_n/
    │   ├── xx-crush-tests.txt
    │   └── alphabit-results.txt
    ├── rabbit_results/
    │   ├── file1.txt
    │   ├── file2.txt
    │   └── filexx..
    └── report.xlsx
```

The folder "nist_results" is generated automatically by the script.
Each "set_n" folder is generated automatically based on the number of binary files to test (one set corresponds to 20 files), and will contain 96 crsuh test .txt files (one for each test) and an alphabit-results.txt.
The "rabbit_results" is generated automatically and will contain one .txt file for each binary file tested.

The report excel will be generated automatically at the end of the tests.

Each $NISTFOLDER contains the results of a specific binary file.
