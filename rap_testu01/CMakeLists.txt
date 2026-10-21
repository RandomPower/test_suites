cmake_minimum_required(VERSION 3.22)
project(rap_testu01 C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# ---------------------------------------------------------------------------
# TestU01 1.2.3 (2009), downloaded at a fixed commit of the official mirror
# and built as static libraries inside the build directory.
#
# - BUILD_IN_SOURCE: TestU01 cannot be built outside its source tree.
# - -std=gnu11: GCC 15 defaults to C23, where the old-style declarations in
#   testu01/ucryptoIS.c no longer compile.
# - ACLOCAL/AUTOCONF/AUTOMAKE/AUTOHEADER=true: the configure script and
#   Makefile.in files were generated in 2009 with autoconf 2.61 and
#   automake 1.10. Git does not keep file timestamps, so make sometimes
#   decides they are out of date and tries to regenerate them, which fails
#   if a newer autoconf is installed. They never need regenerating.
# - Static libraries: the executable does not depend on .so files left in
#   the build directory.
# ---------------------------------------------------------------------------
include(ExternalProject)
include(ProcessorCount)
ProcessorCount(NPROC)
if(NPROC EQUAL 0)
    set(NPROC 1)
endif()

set(TESTU01_PREFIX ${CMAKE_BINARY_DIR}/testu01)
set(TESTU01_INSTALL ${TESTU01_PREFIX}/install)
set(TESTU01_NOREGEN ACLOCAL=true AUTOCONF=true AUTOMAKE=true AUTOHEADER=true)

ExternalProject_Add(testu01_ext
    GIT_REPOSITORY https://github.com/umontreal-simul/TestU01-2009.git
    GIT_TAG a038a868755a75fca4ca8734031335aa0a7f7bcb
    PREFIX ${TESTU01_PREFIX}
    INSTALL_DIR ${TESTU01_INSTALL}
    UPDATE_DISCONNECTED TRUE
    BUILD_IN_SOURCE TRUE
    CONFIGURE_COMMAND <SOURCE_DIR>/configure --prefix=<INSTALL_DIR> --disable-shared
                      CC=${CMAKE_C_COMPILER} "CFLAGS=-O2 -std=gnu11"
    BUILD_COMMAND make -j${NPROC} ${TESTU01_NOREGEN}
    INSTALL_COMMAND make install ${TESTU01_NOREGEN}
    BUILD_BYPRODUCTS ${TESTU01_INSTALL}/lib/libtestu01.a
                     ${TESTU01_INSTALL}/lib/libprobdist.a
                     ${TESTU01_INSTALL}/lib/libmylib.a
)

# Imported targets for the three TestU01 libraries (link order: testu01 -> probdist -> mylib)
file(MAKE_DIRECTORY ${TESTU01_INSTALL}/include)
foreach(lib mylib probdist testu01)
    add_library(TestU01::${lib} STATIC IMPORTED GLOBAL)
    set_target_properties(TestU01::${lib} PROPERTIES
        IMPORTED_LOCATION ${TESTU01_INSTALL}/lib/lib${lib}.a
        INTERFACE_INCLUDE_DIRECTORIES ${TESTU01_INSTALL}/include)
endforeach()
set_property(TARGET TestU01::probdist PROPERTY INTERFACE_LINK_LIBRARIES TestU01::mylib m)
set_property(TARGET TestU01::testu01 PROPERTY INTERFACE_LINK_LIBRARIES TestU01::probdist TestU01::mylib m)

add_subdirectory(src)
