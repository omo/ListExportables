


$ cd WebKit/Source
$ MY_OUT_DIR=`pwd`/tmp MY_CLANG_DIR=~/work/llvm/build/Debug+Asserts/ CC=~/work/llvm/llvm/tools/clang/examples/ListExportables/wrap-clang CXX=~/work/llvm/llvm/tools/clang/examples/ListExportables/wrap-clang xcodebuild -project JavaScriptCore/JavaScriptCore.xcodeproj -configuration Debug clean
$ MY_OUT_DIR=`pwd`/tmp MY_CLANG_DIR=~/work/llvm/build/Release+Asserts/ CC=~/work/llvm/llvm/tools/clang/examples/ListExportables/wrap-clang CXX=~/work/llvm/llvm/tools/clang/examples/ListExportables/wrap-clang xcodebuild -project JavaScriptCore/JavaScriptCore.xcodeproj -configuration Debug -target JavaScriptCore
