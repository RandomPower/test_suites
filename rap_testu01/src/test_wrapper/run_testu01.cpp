#include "run_testu01.hpp"

#include <filesystem>
#include <thread>
#include <functional>
#include <cstdio>
#include <iostream>

extern "C"
{
#include "TestU01.h"
#include <unistd.h>
#include <sys/wait.h>
}

using namespace std;
namespace fs = filesystem;

const vector<Running_Test> TestU01Wrapper::tests_to_run = {
    SERIALOVER_T2, SERIALOVER_T4, COLLISIONOVER_T2, COLLISIONOVER_T2_10, COLLISIONOVER_T4, COLLISIONOVER_T4_20, COLLISIONOVER_T8, COLLISIONOVER_T8_25,
    COLLISIONOVER_T20, COLLISIONOVER_T20_28, SMARSA_BIRTHDAY_SPACINGS_2, SMARSA_BIRTHDAY_SPACINGS_3, SMARSA_BIRTHDAY_SPACINGS_4, SMARSA_BIRTHDAY_SPACINGS_7_0,
    SMARSA_BIRTHDAY_SPACINGS_7_7, SMARSA_BIRTHDAY_SPACINGS_8_14, SMARSA_BIRTHDAY_SPACINGS_8_22, CLOSEPAIRS_2, CLOSEPAIRS_3, CLOSEPAIRS_7, CLOSEPAIRSBITMATCH_2,
    CLOSEPAIRSBITMATCH_4, SIMPOKER_16_0, SIMPOKER_16_26, SIMPOKER_64_0, SIMPOKER_64_24, COUPONCOLLECTOR_4_0, COUPONCOLLECTOR_4_28, COUPONCOLLECTOR_16_0, COUPONCOLLECTOR_16_26,
    GAP_0_0, GAP_27_0, GAP_0_256, GAP_27_256, U01_R0, U01_R15, PERMUTATION_0, PERMUTATION_15, COLLPERMUTATION_0, COLLPERMUTATION_15, MAXOFT_5, MAXOFT_10, MAXOFT_20, MAXOFT_30,
    SAMPLEPROD_10, SAMPLEPROD_30, SAMPLEMEAN, SAMPLECORR, APPEARENCESPACINGS_0, APPEARENCESPACINGS_20, WEIGHTDISTRIB_0, WEIGHTDISTRIB_8, WEIGHTDISTRIB_16, WEIGHTDISTRIB_24,
    SUMCOLLECTOR, MATRIXRANK_60x60_0, MATRIXRANK_60x60_1, MATRIXRANK_300x300_0, MATRIXRANK_300x300_1, MATRIXRANK_1200x1200_0, MATRIXRANK_1200x1200_1, SAVIR2, GCD_0, GCD_10,
    RWALK_L90_0, RWALK_L90_1, RWALK_L1000_0, RWALK_L1000_1, RWALK_L10000_0, RWALK_L10000_1, LINEARCOMP_0, LINEARCOMP_29, LEMPELZIV, FOURIER3_0, FOURIER3_20, LONGEST_HEAD_0, LONGEST_HEAD_20,
    PERIOD_IN_STRINGS_0, PERIOD_IN_STRINGS_15, HAMMING_WEIGHT_2_0, HAMMING_WEIGHT_2_20, HAMMING_CORR_30, HAMMING_CORR_300, HAMMING_CORR_1200, HAMMING_INDEP_30_0_30,
    HAMMING_INDEP_30_20_30, HAMMING_INDEP_300_0_30, HAMMING_INDEP_300_20_30, HAMMING_INDEP_1200_0_30, HAMMING_INDEP_1200_20_30, STRING_RUN_0_30, STRING_RUN_20_10, AUTOCOR_0_30_1,
    AUTOCOR_20_10_1, AUTOCOR_0_30_30, AUTOCOR_20_10_10};

// Define a free function
unsigned long getBytesCallback(void *param)
{
    return static_cast<FileStruct *>(param)->getBytes();
};

void TestU01Wrapper::RunCrush(vector<FileStruct> *sets)
{
    for (size_t set = 0; set < sets->size(); set++)
    {
        for (auto test = tests_to_run.begin(); test < tests_to_run.end(); test++)
        {
            pid_t pid = fork();
            if (pid == 0)
            {
                FileStruct set_copy((*sets)[set]);
                set_copy.setTest(*test);

                const string out_filename = set_copy.getDirectory() + "/" + to_string(set_copy.getTestNumber()) + "-output-crush-multi.txt";
                int stdout_fd = dup(fileno(stdout));
                FILE *out = freopen(out_filename.c_str(), "w", stdout);

                set_copy.setCurrentInstance(&set_copy);
                unif01_Gen *gen = unif01_CreateExternGenBits((char *)"CRUSH-MULTI", FileStruct::getBytesStatic);
                bbattery_RepeatCrush(gen, set_copy.getRepVector());
                unif01_DeleteExternGenBits(gen);

                cout << "====================Test End====================" << endl;

                fflush(stdout);
                dup2(stdout_fd, fileno(stdout));
                close(stdout_fd);
                fclose(out);
                exit(0);
            }
        }

        // Waits for all forked process to end before moving on to the next set
        int status = 0;
        while (wait(&status) > 0)
            ;
    }
}

void TestU01Wrapper::RunAlphabit(vector<FileStruct> *sets)
{
    for (size_t set = 0; set < sets->size(); set++)
    {
        pid_t pid = fork();
        if (pid == 0)
        {
            auto cur_set = (*sets)[set];
            const string out_filename = cur_set.getDirectory() + "/alphabit-output.txt";
            int stdout_fd = dup(fileno(stdout));
            FILE *out = freopen(out_filename.c_str(), "w", stdout);

            const string destFile = cur_set.getDirectory() + "/alphabit.bin";
            auto files = cur_set.getFileNames();

            ofstream dest(destFile, ios::binary | ios::trunc);
            if (!dest)
            {
                cerr << "Alphabit: Error Opening destination file: " << destFile << endl;
                exit(EXIT_FAILURE);
            }

            for (const auto &srcfile : files)
            {
                ifstream src(srcfile, ios::binary);
                if (!src)
                {
                    cerr << "Alphabit: Error Opening source file: " << srcfile << endl;
                    exit(EXIT_FAILURE);
                }
                dest << src.rdbuf();
            }
            dest.close();

            ifstream in_file(destFile, ios::binary | ios::ate);
            if (!in_file)
            {
                cerr << "Alphabit: Error Opening concatenated file: " << destFile << endl;
                exit(EXIT_FAILURE);
            }
            streamsize file_size = in_file.tellg();
            in_file.close();

            // Multiply size by 8: test requires size in bits
            bbattery_AlphabitFile(const_cast<char *>(destFile.c_str()), static_cast<double>(file_size * 8));

            remove(destFile.c_str());

            cout << "====================Test End====================" << endl;

            fflush(stdout);
            dup2(stdout_fd, fileno(stdout));
            close(stdout_fd);
            fclose(out);
            exit(0);
        }
    }

    // Wait for all children
    int status = 0;
    while (wait(&status) > 0)
        ;
}

void TestU01Wrapper::RunRabbit(vector<string> *bin_files)
{
    string dir_name = "rabbit_results";
    if (!fs::exists(dir_name))
    {
        fs::create_directory(dir_name);
    }

    for (size_t i = 0; i < bin_files->size(); i++)
    {
        pid_t pid = fork();
        if (pid == 0)
        {
            const string bin_file = (*bin_files)[i];
            filesystem::path bin_path(bin_file);
            string bin_name = bin_path.stem().string();

            const string out_filename = dir_name + "/" + bin_name + "-output.txt";
            int stdout_fd = dup(fileno(stdout));
            FILE *out = freopen(out_filename.c_str(), "w", stdout);

            ifstream in_file(bin_file, ios::binary | ios::ate);
            if (!in_file)
            {
                cerr << "Alphabit: Error Opening concatenated file: " << bin_file << endl;
                exit(EXIT_FAILURE);
            }
            streamsize file_size = in_file.tellg();
            in_file.close();

            bbattery_RabbitFile(const_cast<char *>(bin_file.c_str()), static_cast<double>(file_size));

            cout << "====================Test End====================" << endl;

            fflush(stdout);
            dup2(stdout_fd, fileno(stdout));
            close(stdout_fd);
            fclose(out);
            exit(0);
        }

        // Add a limit of 20 processes at the time
        if (i % 20 == 0 || i >= bin_files->size()) 
        {
            int status = 0;
            while (wait(&status) > 0)
                ;
        }
    }
}