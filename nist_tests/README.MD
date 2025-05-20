Run the make command to generate the assess executable. 
```
make
```

The ./assess and ./run_nist_tests.sh scripts and the ./templates folder must be placed in a generic directory where anybody can have access to run the NIST tests.
The NIST_ASSESS_DIR variable in the run_nist_tests.sh script must be set to the directory where the assess script is located.
For example, in /usr/local/bin/, the structure will look as follows:

```
/usr/local/bin/
    └── nist/
        ├── assess
        ├── run_nist_tests.sh/
        └── templates/
```

The assess and run_nist_tests scripts must be executable. You can do this by running the following command:

```
chmod +x assess
chmod +x run_nist_tests.sh
```

Set the workspace to be the folder where you want the results to be generated.
There must be a folder called "binaries" or "bins" containing the binaries in the workspace.

The structure of the folders is as follows:

```
main_worskpace/
    ├── binaries/
    │   ├── binary1
    │   └── binary2
    └── nist_results/
        └── $NISTFOLDER/
            ├── etc/
            └── etc2/
```

The folder "nist_results" is generated automatically by the script.
Each $NISTFOLDER contains the results of a specific binary file.
