# Compile the nist test suite
cd nist_tests
make
chmod +x assess
chmod +x run_nist_tests.sh
cd ..

# Copy the files in final executable folder
cp ./nist_tests/assess ./test_lib/nist/
cp ./nist_tests/run_nist_tests.sh ./test_lib/nist/
rsync -avz ./nist_tests/templates ./test_lib/nist/

# Compile the TestU01 library and test runner
cd rap_testu01
chmod +x builder.sh
./builder.sh
chmod +x ./build/src/rap_testu01 
cd ..

# Set environment and create report generator
cd report_generator
chmod +x build.sh
./build.sh
cd ..

cp ./report_generator/dist/report_generator ./test_lib

# Copy the TestU01 runner in the new folder
cp ./rap_testu01/build/src/rap_testu01 ./test_lib/testu01

sudo mv ./test_lib /usr/local/bin/test_lib