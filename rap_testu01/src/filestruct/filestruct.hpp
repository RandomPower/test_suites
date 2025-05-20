#pragma once

#include <vector>
#include <string>
#include <fstream>

#include "tests.hpp"

using namespace std;

const u_int8_t MAX_FILES = 20;

class FileStruct
{
    static FileStruct* current_instance;
private:
    string results_directory;
    u_int8_t num_files;
    vector<string> file_names;
    u_int32_t total_bytes;

    u_int8_t cur_file_idx;
    ifstream file_stream;
    size_t cur_file_length;
    u_int32_t current_position;

    Running_Test test;
    u_int32_t repetitions;
    int rep_vector[CRUSH_NUM + 1];

public:
    FileStruct();
    FileStruct(const FileStruct &other);
    ~FileStruct();
    
    void addFile(const string &file_name);
    void openFile();
    
    static void setCurrentInstance(FileStruct* instance) { current_instance = instance; }
    static u_int32_t getBytesStatic();
    u_int32_t getBytes();

    void calculateTotalBytes();
    u_int32_t getTotalBytes();

    void setTest(Running_Test test);
    void CalculateRepetitions();
    void SetTestRequiredCount();

    void setDirectory(string dir)
    {
        this->results_directory = dir;
    }

    int getTestNumber()
    {
        return this->test.test_number;
    }

    string getDirectory()
    {
        return this->results_directory;
    }
    
    int* getRepVector() {
        return rep_vector;
    }

    vector<string> getFileNames() {
        return file_names;
    }
};
