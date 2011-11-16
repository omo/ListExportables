#!/usr/bin/bash

BUILD_ROOT=$1
HERE=`dirname $0`
BUILD_DIR=${BUILD_ROOT}/tools/clang/examples/ListExportables/

mkdir -p ${BUILD_ROOT}/tools/clang/examples/ListExportables/
cp ${HERE}/Makefile ${BUILD_DIR}/Makefile
