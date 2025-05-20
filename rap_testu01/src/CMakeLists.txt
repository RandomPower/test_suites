# Main project
set(SOURCES main.cpp)

find_package(OpenMP REQUIRED)

set(TESTU01_ROOT ../testu01lib)
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
