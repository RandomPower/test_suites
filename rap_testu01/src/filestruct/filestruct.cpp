#include "filestruct.hpp"

#include <cmath>
#include <iostream>

using namespace std;

FileStruct* FileStruct::current_instance = nullptr;

FileStruct::FileStruct()
{
    num_files = 0;
    total_bytes = 0;
    cur_file_idx = 0;
    current_position = 0;
    cur_file_length = 0;
    file_stream.clear();
}

FileStruct::FileStruct(const FileStruct &other)
{
    results_directory = other.results_directory;
    num_files = other.num_files;
    file_names = other.file_names;
    total_bytes = other.total_bytes;
    cur_file_idx = other.cur_file_idx;
    cur_file_length = other.cur_file_length;
    current_position = other.current_position;
    test = other.test;
}

FileStruct::~FileStruct()
{
}

void FileStruct::addFile(const string &file_name)
{
    if (num_files >= MAX_FILES)
    {
        cout << "Maximum number of files reached." << endl;
        return;
    }

    file_names.push_back(file_name);
    num_files++;
}

void FileStruct::openFile()
{
    if (file_stream.is_open())
    {
        file_stream.close();
    }

    if (cur_file_idx >= num_files)
    {
        cout << "No more files to open." << endl;
        return;
    }

    file_stream.open(file_names[cur_file_idx], ios::binary);
    if (!file_stream.is_open())
    {
        cout << "Failed to open file: " << file_names[cur_file_idx] << endl;
        return;
    }

    file_stream.seekg(0, ios::end);
    cur_file_length = file_stream.tellg() / sizeof(u_int32_t); // - 1;
    file_stream.seekg(0, ios::beg);

    current_position = 0;
    cout << "Opened file: " << file_names[cur_file_idx] << endl;
    cout << "File length (bytes): " << cur_file_length << endl;
}

u_int32_t FileStruct::getBytesStatic() {
    return current_instance->getBytes();
}

u_int32_t FileStruct::getBytes()
{
    if (!file_stream.is_open() || file_stream.eof() || current_position >= cur_file_length)
    {
        openFile();
    }

    u_int32_t data;
    file_stream.read(reinterpret_cast<char *>(&data), sizeof(u_int32_t));
    current_position++;

    if (file_stream.eof() || current_position >= cur_file_length)
    {
        cur_file_idx++;
    }

    return data;
}

void FileStruct::calculateTotalBytes()
{
    u_int32_t total_bytes = 0;
    for (const auto &file_name : file_names)
    {
        ifstream temp_stream(file_name, ios::binary);
        if (temp_stream.is_open())
        {
            temp_stream.seekg(0, ios::end);
            total_bytes += temp_stream.tellg() / sizeof(u_int32_t);
            temp_stream.close();
        }
    }

    this->total_bytes = total_bytes;
}

u_int32_t FileStruct::getTotalBytes()
{
    return this->total_bytes;
}

void FileStruct::setTest(Running_Test test)
{
    if (total_bytes == 0)
    {
        calculateTotalBytes();
    }

    this->test = test;
    CalculateRepetitions();
    SetTestRequiredCount();
}

void FileStruct::CalculateRepetitions()
{
    repetitions = floor(this->total_bytes / this->test.test_size);
    if (repetitions < 1)
    {
        repetitions = 1;
    }
}

void FileStruct::SetTestRequiredCount()
{
    for (int i = 0; i < CRUSH_NUM + 1; i++)
    {
        rep_vector[i] = 0;
    }

    int a = test.test_size;

    cout << "Required numbers for test: " << test.test_number << " is " << a << endl;
    cout << "Total bytes available: " << total_bytes << endl;
    cout << "Repeat test: " << test.test_number << " for " << repetitions << " times " << endl;

    for (int i = 0; i < CRUSH_NUM + 1; i++)
    {
        if (i == test.test_number)
        {
            rep_vector[i] = repetitions;
            if (i == 71 || i == 72 || i == 73)
            {
                rep_vector[i] = 1;
            }
        }
        else
        {
            rep_vector[i] = 0;
        }
    }
}