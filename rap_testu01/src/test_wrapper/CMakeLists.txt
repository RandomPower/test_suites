add_library(run_testu01)

target_sources(run_testu01
    PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}/run_testu01.cpp
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/run_testu01.hpp
    )

target_include_directories(run_testu01
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}
    )

    
target_link_libraries(run_testu01
    PUBLIC
        filestruct
    )