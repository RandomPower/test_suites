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

`install.sh` (in the repository root) builds and installs everything. To build only `assess`:

```
make
```

`install.sh` copies `assess`, `run_nist_tests.sh` and the `templates` folder to:

```
/usr/local/bin/test_lib/
    └── nist/
        ├── assess
        ├── run_nist_tests.sh
        └── templates/
```

`run_nist_tests.sh` looks for `assess` and `templates` in `/usr/local/bin/test_lib/nist`; set the
environment variable `NIST_ASSESS_DIR` to use another folder.

## Running

The NIST tests are normally started together with the other suites by `raptests` (see the main README).
To run only the NIST tests, run `run_nist_tests.sh` from the workspace, the folder that contains a
"binaries" or "bins" folder with the `.bin` files.

Each `.bin` file is tested with `assess 1000000 -i <file> -f 1 -n 2000`: 2000 streams of 10^6 bits,
so every file must contain at least 2*10^9 bits (250 MB).

Parallelism: one `assess` runs per `.bin` file, at most one per core. When there are fewer files than
cores, the spare cores go to OpenMP, which runs the 15 tests of each stream in parallel (at most 15
threads per file). On a 64-core server, 64 or more files run single-threaded, 64 at a time, while
8 files get 8 threads each. Set `NIST_CORES` to use fewer cores, e.g. when the server is shared.

The structure of the folders is as follows:

```
main_workspace/
    ├── binaries/
    │   ├── binary1.bin
    │   └── binary2.bin
    └── nist_results/
        └── $NISTFOLDER/
            ├── log.txt
            └── AlgorithmTesting/
                ├── finalAnalysisReport.txt
                ├── freq.txt
                ├── Frequency/
                ├── ...
                └── RandomExcursionsVariant/
```

The folder "nist_results" is generated automatically by the script.
Each $NISTFOLDER is named after a binary file and contains its results: one folder per test, with
`stats.txt` and `results.txt` (the p-values), and the summary in `finalAnalysisReport.txt`.
