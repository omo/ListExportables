#!/usr/bin/env python

import sys
import json
import re
from optparse import OptionParser

attribue_name = "JSC_PRIVATE_EXPORT"

class Symbol:
    def __init__(self, symbol_dict):
        self.dict = symbol_dict

    @property
    def value(self):
        return self.dict["symbol"]

    @property
    def valueType(self):
        return self.dict["type"]

    def guess_location(self):
        candidates = self.dict["locations"]
        of_headers = [ loc for loc in candidates if re.search(r'\.h$', loc[0]) ]
        if of_headers:
            # chooses the earliest one.
            of_headers.sort(lambda x, y: x[1] - y[1])
            return of_headers[0]
        candidates.sort(lambda x, y: x[1] - y[1])
        return candidates[0]


def make_rewrite_line(symbol, line, column):
    if symbol.valueType == "RecordDecl":
        return line[0:column] + ("%s " % attribue_name) + line[column:]
    if symbol.valueType in [ "CXXConstructorDecl", 
                             "CXXDestructorDecl",
                             "CXXMethodDecl",
                             "FunctionDecl",
                             "VarDecl" ]:
        m = re.search(r'\S', line)
        return line[:m.start(0)] + ("%s " % attribue_name) + line[m.start(0):]
    raise Exception("Unknown valueType:%s" % symbol.valueType)
    

def apply_symbol_rewrite(symbol, options):
    locaton = symbol.guess_location()
    src = open(locaton[0])
    lines = src.readlines()
    src.close()
    target = lines[locaton[1] - 1] # original vaue is 1-origin
    if options.verbose:
        print ("# %s(%s) -> %s:%d" % (symbol.value, symbol.valueType, locaton[0], locaton[1]))
        print "BEFORE:", target.strip()
        print "AFTER: ", make_rewrite_line(symbol, target, locaton[2] - 1).strip() # original value is 1-origin

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
