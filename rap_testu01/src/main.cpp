#include <iostream>
#include <filesystem>
#include <vector>

#include "filestruct/filestruct.hpp"
#include "test_wrapper/run_testu01.hpp"

using namespace std;
namespace fs = filesystem;

void createFileStructsFromBins(vector<string> &bin_files, vector<FileStruct> &sets)
{

    string dir_name;
    if (fs::exists("bins") && fs::is_directory("bins"))
    {
        dir_name = "bins";
    }
    else if (fs::exists("binaries") && fs::is_directory("binaries"))
    {
        dir_name = "binaries";
    }
    else
    {
        cerr << "No 'bins' or 'binaries' directory found." << endl;
    }

    for (const auto &entry : fs::directory_iterator(dir_name))
    {
        if (entry.is_regular_file() && entry.path().extension() == ".bin")
        {
            bin_files.push_back(entry.path().string());
        }
    }

    for (size_t i = 0; i < bin_files.size(); i += 20)
    {
        FileStruct fs;
        for (size_t j = i; j < i + 20 && j < bin_files.size(); ++j)
        {
            fs.addFile(bin_files[j]);
        }
        sets.push_back(fs);
    }
}

int main()
{
    /*
        First: list all the .bin files in the directory and group them by 20
    */
    vector<string> bin_files;
    vector<FileStruct> sets;
    createFileStructsFromBins(bin_files, sets);

    /*
        Second: for each group of 20, create a directory called "set_<index>" where to store the results
        of the tests
    */
    for (size_t i = 1; i <= sets.size(); ++i)
    {
        string dir_name = "set_" + to_string(i);
        if (!fs::exists(dir_name))
        {
            fs::create_directory(dir_name);
        }

        sets[i - 1].setDirectory(dir_name);
    }

    /*
        Third: run the CRUSH test on each set of 20 files.
        The tests are 96, we want them to run in parallel and store the results on different output files
        in the directories created in the previous step. Therefore we create a copy of the struct vector and assign
        a test to each copy.
    */
    TestU01Wrapper::RunCrush(&sets);

    /*
        Fourth: run the Alphabit test on each set of 20 files.
    */
    TestU01Wrapper::RunAlphabit(&sets);

    /*
        Fifth: run the Rabbit test on each file separately.
    */
    TestU01Wrapper::RunRabbit(&bin_files);
    return 0;
}