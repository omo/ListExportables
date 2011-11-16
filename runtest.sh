#!/usr/bin/bash

#BUILD_ROOT=$1
BUILD_ROOT=../../../../../build
CLANGCXX=${BUILD_ROOT}/Debug+Asserts/bin/clang++
CLANGCXX=${BUILD_ROOT}/Debug+Asserts/bin/clang++
BUILD_DIR=${BUILD_ROOT}/tools/clang/examples/ListExportables/
TESTSRC=hello.cpp
MAKE_FLAGS="ENABLE_OPTIMIZED=1"
PLUGIN_FLAGS="-add-plugin list-exp"
#PLUGIN_FLAGS="-plugin list-exp -plugin-arg-list-exp hello.symbols"

make -C ${BUILD_DIR} ${MAKE_FLAGS}
make -C ${BUILD_DIR}
${CLANGCXX} -cc1 -load ${BUILD_ROOT}/Debug+Asserts/lib/libListExportables.dylib ${PLUGIN_FLAGS} ${TESTSRC}
