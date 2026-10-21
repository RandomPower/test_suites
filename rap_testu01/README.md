Run builder.sh to compile the TestU01 library and to link it with the test runner
```
./builder.sh
```

TestU01 is not stored in this repository: CMake downloads the official TestU01 1.2.3
sources (https://github.com/umontreal-simul/TestU01-2009, fixed commit `a038a86`) and
builds them as static libraries inside `build/`. Requirements: git, make,
cmake >= 3.22 and access to github.com during the build. See the comments in
`CMakeLists.txt` for the build options that make TestU01 compile with recent
compilers (GCC 15) and autotools.

The executable is created in `build/src/rap_testu01`. `install.sh` (in the repository root) builds it and
installs it as `/usr/local/bin/test_lib/testu01`. TestU01 is linked statically, so the executable does not
depend on any file left in the build folder.

Set the workspace to be the folder where you want the results to be generated.
There must be a folder called "binaries" or "bins" containing the binaries in the workspace.

The structure of the folders is as follows:

```
main_workspace/
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
