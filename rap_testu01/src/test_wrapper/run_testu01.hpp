#pragma once

#include <vector>

#include "../filestruct/filestruct.hpp"

using namespace std;
class TestU01Wrapper
{
public:
    const static std::vector<Running_Test> tests_to_run;

    static void RunCrush(vector<FileStruct> *sets);
    static void RunAlphabit(vector<FileStruct> *sets);
    static void RunRabbit(vector<string> *bin_files);
};