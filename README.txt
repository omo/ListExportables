
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

At first, use the Clang plugin to generate the possibly exported symbols.

  $ export WORK_ROOT=`pwd`
  $ export TOOL_ROOT=$WORK_ROOT/llvm/tools/clang/examples/ListExportables/
  $ cd ...somewhere.../WebKit/Source # Assuming you have a WebKit checkout.
  $ mkdir -p tmp
  $ MY_OUT_DIR=`pwd`/tmp MY_CLANG_DIR=$WORK_ROOT/build/Release+Asserts/ \
    CC=$TOOL_ROOT/wrap-clang  CXX=$TOOL_ROOT/wrap-clang \
    xcodebuild -project JavaScriptCore/JavaScriptCore.xcodeproj -configuration Debug -target JavaScriptCore

Then accumulate and filter it to find out the symbol's locations to rewrite.

  $ $TOOL_ROOT/symbols-to-locations.py -f JavaScriptCore/build/Debug/DerivedSources/JavaScriptCore/JavaScriptCore.JSVALUE64.exp \
     tmp/*.l2s > tmp/JavaScriptCore.s2l

Rewrite the code. The rewiter uses the result of the previous step.

  $ $TOOL_ROOT/rewrite.py tmp/JavaScriptCore.s2l

Even after the rewrite, we should be able to build it as usual.

WebKit patches:
-------------------------------------

To build .exp-less JSC, you need following patches applied:

 * https://bugs.webkit.org/show_bug.cgi?id=72854 to remove exp file from the build.
 * https://bugs.webkit.org/show_bug.cgi?id=72862 to relax build validation check.
 * https://bugs.webkit.org/show_bug.cgi?id=72853 to add missing macros.
 * https://bugs.webkit.org/show_bug.cgi?id=72858 to fix wrong code.

