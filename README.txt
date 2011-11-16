


To run:

  $ cd WebKit/Source
  $ mkdir -p tmp
  $ export TOOL_ROOT=~/work/llvm/llvm/tools/clang/examples/ListExportables/
  $ MY_OUT_DIR=`pwd`/tmp MY_CLANG_DIR=~/work/llvm/build/Release+Asserts/ \
    CC=$TOOL_ROOT/wrap-clang  CXX=$TOOL_ROOT/wrap-clang \
    xcodebuild -project JavaScriptCore/JavaScriptCore.xcodeproj -configuration Debug -target JavaScriptCore
  $ $TOOL_ROOOT/symbols-to-locations.py -f JavaScriptCore/JavaScriptCore.exp tmp/*.l2s > tmp/JavaScriptCore.s2l
