# Main project
set(SOURCES main.cpp)

find_package(OpenMP REQUIRED)

add_executable(rap_testu01 ${SOURCES})

# Module subdirectories
add_subdirectory(filestruct)
add_subdirectory(test_wrapper)

target_link_libraries(rap_testu01
    PRIVATE
        run_testu01
        filestruct
        TestU01::testu01
)

# TestU01 must be downloaded and built before anything that includes its headers
add_dependencies(run_testu01 testu01_ext)
add_dependencies(rap_testu01 testu01_ext)
