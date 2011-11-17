#!/usr/bin/bash

BUILD_ROOT=../../../../../build
CLANGCXX=${BUILD_ROOT}/Debug+Asserts/bin/clang++
CLANGCXX=${BUILD_ROOT}/Debug+Asserts/bin/clang++
BUILD_DIR=${BUILD_ROOT}/tools/clang/examples/ListExportables/
TESTSRC=hello.cpp
MAKE_FLAGS="ENABLE_OPTIMIZED=1"
PLUGIN_FLAGS="-add-plugin list-exp"
#PLUGIN_FLAGS="-plugin list-exp -plugin-arg-list-exp hello.symbols"
L2SFILE=hello.l2s
S2LFILE=hello.s2l

make -C ${BUILD_DIR} ${MAKE_FLAGS}
make -C ${BUILD_DIR}
${CLANGCXX} -cc1 -load ${BUILD_ROOT}/Debug+Asserts/lib/libListExportables.dylib ${PLUGIN_FLAGS} ${TESTSRC} | tee ${L2SFILE} > /dev/null
python symbols-to-locations.py -v ${L2SFILE} | tee ${S2LFILE} > /dev/null

cp hello.cpp hello.cpp.bak
cp hello.h hello.h.bak

python rewrite.py ${S2LFILE}

cat hello.h
cat hello.cpp
${CLANGCXX} -c hello.cpp

mv hello.cpp.bak hello.cpp
mv hello.h.bak hello.h
