add_library(filestruct)

target_sources(filestruct
    PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}/filestruct.cpp
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/filestruct.hpp
    )

target_include_directories(filestruct
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}
    )
