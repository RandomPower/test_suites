Run builder.sh to compile the TestU01 library and to link it with the test runner
```
./builder.sh
```

The ./rap_testu01 executable must be placed in a generic directory where anybody can have access to run the tests.
For example, in /usr/local/bin/, the structure will look as follows:

```
/usr/local/bin/
    └── testu01/
        └── rap_testu01
```

The rap_testu01 must have execution rights. You can do this by running the following command:

```
chmod +x rap_testu01
```

Set the workspace to be the folder where you want the results to be generated.
There must be a folder called "binaries" or "bins" containing the binaries in the workspace.

The structure of the folders is as follows:

```
main_worskpace/
    ├── binaries/
    │   ├── binary1
    │   └── binary2
    ├── set_1/
    │   ├── xx-crush-tests.txt
    │   └── alphabit-results.txt
    └── rabbit_results/
        ├── file1.txt
        ├── file2.txt
        └── filexx..
```
Each "set_xx" folder is generated automatically based on the number of binary files to test (one set corresponds to 20 files).
The "rabbit_results" is generated automatically and will contain one .txt file for each binary file tested.
