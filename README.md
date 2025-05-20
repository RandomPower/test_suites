# NIST and TestU01 Libraries
Repo containing an automatic procedure to run the NIST test suite and TestU01 with creation of a final analysis Excel report

## Installation
Navigate with the terminal into the test_suites directory and run the following commands to automatically compile the NIST and TestU01 libraries and to move them in /usr/local/bin/
Admin powers will be required for this last operation.

```
chmod +x runMe.sh
./runMe.sh
```

The generated executables will be moved into /usr/local/bin/ and will have the following structure:

```
/usr/local/bin/
    ├── nist/
    │   ├── assess
    │   ├── run_nist_tests.sh/
    │   └── templates/
    └── testu01/
        └── rap_testu01
```

## Running the tests
Set the workspace to be the folder where you want the results to be generated.
There must be a folder called "binaries" or "bins" containing the binaries in the workspace.

To run the tests, run the following command:

```
nohup /usr/local/bin/runtests.sh &
```
As the tests will take a lot of time, this will ensure that they are ran in background.

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
