# Main project
set(SOURCES main.cpp)

find_package(OpenMP REQUIRED)

# Set paths for TestU01
set(TESTU01_ROOT ${CMAKE_CURRENT_LIST_DIR}/../testu01lib)
include_directories(${TESTU01_ROOT}/include)
link_directories(${TESTU01_ROOT}/lib)

add_executable(rap_testu01 ${SOURCES})

# Module subdirectories
add_subdirectory(filestruct)
add_subdirectory(test_wrapper)

target_link_libraries(rap_testu01
    PRIVATE
        run_testu01
        filestruct
        testu01
        probdist
        mylib
)