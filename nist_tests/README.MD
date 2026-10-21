# NIST STS 2.1.2 (RaP version)

This folder contains the NIST Statistical Test Suite 2.1.2 (SP 800-22 Rev. 1a),
imported unchanged from the official `sts-2_1_2.zip` in the commit tagged
`nist-sts-2.1.2`, plus our changes on top. To see every change we made to the
NIST code:

```
git diff nist-sts-2.1.2 -- nist_tests
```

Our changes:

- `assess` runs non-interactively
  (`assess <stream length> -i <file> -f <0 ASCII|1 binary> -n <number of streams>`)
  and writes its results under `nist_results/$NISTFOLDER/`;
- the 15 tests of each bitstream run in parallel with OpenMP;
- faster counting in Linear Complexity (Berlekamp-Massey on 64-bit words),
  Non-overlapping Template, Serial and Approximate Entropy (sliding-window
  integers instead of bit-by-bit loops). These only change how an exact integer
  count is computed: statistics, p-values and output files are the same as the
  original, byte for byte, and about 8 times faster on a single core.

### Verifying against the original

`verify_against_original.sh` builds the original NIST STS 2.1.2 from the
`nist-sts-2.1.2` tag and this version, runs both on the same file with all
15 tests, and compares every output file byte by byte:

```
nist_tests/verify_against_original.sh <file.bin> [num_bitstreams] [stream_length]
```

Run it after any change to the code in this folder.

## Build and installation

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
