
Building:
----------

Build Clang: (See http://clang.llvm.org/get_started.html for more details.)

  $ cd $WORK_ROOT
  $ git clone http://llvm.org/git/llvm.git
  $ cd llvm/tools
  $ git clone git clone http://llvm.org/git/clang.git
  $ cd .. # back to the root
  $ mkdir -p build
  $ cd build
  $ configure ../llvm/configure
  $ make ENABLE_OPTIMIZED=1

Build this tool:

  $ git clone https://github.com/omo/ListExportables ./llvm/tools/clang/examples/ListExportables
  $ mkdir -p ./build/tools/clang/examples/ListExportables/
  $ cp ./llvm/tools/clang/examples/ListExportables/Makefile ./build/tools/clang/examples/ListExportables/
  $ make -C ./build/tools/clang/examples/ListExportables/ ENABLE_OPTIMIZED=1

Running against JavaScriptCore:
--------------------------------

First the Clang plugin generate the possibly exported symbols.

  $ cd ..somewhere.../WebKit/Source # Assuming you have a WebKit checkout.
  $ mkdir -p tmp
  $ export TOOL_ROOT=$WORK_ROOT/llvm/tools/clang/examples/ListExportables/
  $ MY_OUT_DIR=`pwd`/tmp MY_CLANG_DIR=$WORK_ROOT/build/Release+Asserts/ \
    CC=$TOOL_ROOT/wrap-clang  CXX=$TOOL_ROOT/wrap-clang \
    xcodebuild -project JavaScriptCore/JavaScriptCore.xcodeproj -configuration Debug -target JavaScriptCore

Then accumulate and filter it to find out the symbol's locations to rewrite.

  $ $TOOL_ROOOT/symbols-to-locations.py -f JavaScriptCore/JavaScriptCore.exp tmp/*.l2s > tmp/JavaScriptCore.s2l

With the result of the previous step, now we can run the rewriter.

  $ $TOOL_ROOOT/rewrite.py tmp/JavaScriptCore.s2l


