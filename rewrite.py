#!/usr/bin/env python
# Copyright (C) 2011 Google Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import json
import re
from optparse import OptionParser

attribue_name = "JSC_PRIVATE_EXPORT"
skip_pattern = re.compile(r'_EXPORT|ALWAYS_INLINE|HIDDEN_INLINE')

def find_macro_name(symbol, filename):
    if 0 <= filename.find("/wtf/"):
        if symbol.rewrite_as == "inline":
            return "HIDDEN_INLINE"
        else:
            return "WTF_EXPORT_PRIVATE"
    if 0 <= filename.find("/JavaScriptCore/"):
        if symbol.kind == "VarDecl":
            return "JS_EXPORTDATA"
        else:
            if symbol.rewrite_as == "inline":
                return "HIDDEN_INLINE"
            else:
                return "JS_EXPORT_PRIVATE"
    # For ease to debug
    if symbol.rewrite_as == "inline":
        return "MY_INLINE"
    else:
        return "MY_EXPORT_PRIVATE" # For testing.


class Symbol:
    def __init__(self, symbol_dict):
        self.dict = symbol_dict

    @property
    def value(self):
        return self.dict["symbol"]

    @property
    def rewrite_as(self):
        return self.dict["rewrite"]

    @property
    def kind(self):
        return self.dict["kind"]

    @property
    def locations(self):
        return self.dict["locations"]

    def make_rewrite_line(self, line, filename, column):
        if skip_pattern.search(line):
            return line
        macro_name = find_macro_name(self, filename)
        if self.kind == "RecordDecl":
            return line[0:column] + ("%s " % macro_name) + line[column:]
        if self.kind in [ "CXXConstructorDecl", 
                          "CXXDestructorDecl",
                          "CXXMethodDecl",
                          "FunctionDecl",
                          "VarDecl" ]:
            if self.rewrite_as == "inline":
                m = re.search(r'^\s*(inline\s*)', line)
                if m:
                    line = line[:m.start(1)] + line[m.end(1):]
            start = 0
            extern_c_match = re.match(r'extern\s+"C"', line)
            if extern_c_match:
                start = extern_c_match.end(0)
            pattern = re.compile(r'\S')
            m = pattern.search(line, start)
            return line[:m.start(0)] + ("%s " % macro_name) + line[m.start(0):]
        raise Exception("Unknown valueType:%s" % symbol.valueType)


def apply_symbol_rewrite(symbol, options):
    for loc in symbol.locations:
        src = open(loc[0])
        lines = src.readlines()
        src.close()
        index = loc[1] - 1
        original = lines[index] # original vaue is 1-origin
        modified = symbol.make_rewrite_line(original, loc[0], loc[2] - 1)
        if options.verbose:
            print ("# %s(%s) -> %s:%d" % (symbol.value, symbol.kind, loc[0], loc[1]))
            print "BEFORE:", original.strip()
            print "AFTER: ", modified.strip() # original value is 1-origin
            print ""
        if not options.preview:
            lines[index] = modified
            dst = open(loc[0], "w")
            dst.write("".join(lines))
            dst.close()
    

if __file__ == sys.argv[0]:
    parser = OptionParser()
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Print status messages to stdout")
    parser.add_option("-p", "--preview",
                      action="store_true", dest="preview", default=False,
                      help="Print preview without modifying files")
    (options, args) = parser.parse_args()
    symbols_file = args[0]
    root = json.load(open(symbols_file))
    symbols = [Symbol(s) for s in root["symbols"] if s]
    for s in symbols:
        apply_symbol_rewrite(s, options)
