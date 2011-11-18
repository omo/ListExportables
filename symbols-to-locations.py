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
from optparse import OptionParser

class Location:
    def __init__(self, location_dict):
        self.dict = location_dict

    @property
    def location(self):
        return self.dict["location"]

    @property
    def symbols(self):
        return self.dict["symbols"]

    @property
    def kind(self):
        return self.dict["kind"]

    @property
    def name(self):
        return self.dict["name"]

    @property
    def definition(self):
        return "definition" in self.dict["options"]


    def __eq__(self, other):
        return self.location == other.location and self.symbols == other.symbols


class Symbol:
    def __init__(self, name):
        self.rewrite = None
        self.symbol = name
        self.locations = []

    def add_location(self, loc):
        if not self.locations.count(loc):
            self.locations.append(loc)

    @property
    def kind(self):
        return self.locations[0].kind

    @property
    def name(self):
        return self.locations[0].name

    @property
    def parent(self):
        return self.locations[0].dict.get("parent")

    @property
    def inlined(self):
        return "inlined" in self.locations[0].dict["options"]

    @property
    def locations_to_rewrite(self):
        if self.kind == "RecordDecl":
            assert(len(self.locations) == 1) # The plugin sould only dump the definition, which should be single place.
            assert(self.locations[0].definition)
            return self.locations
        # Prefer declaration if we have both.
        declarations = [ c for c in self.locations if not c.definition ]
        if declarations:
            return declarations
        # If there is no declaration, it should be the single definiton.
        assert(1 == len(self.locations))
        return self.locations

    def mark_rewrite_as(self, value):
        self.rewrite = value

    def to_json(self):
        return { "symbol": self.symbol, "name": self.name, "kind": self.kind,
                 "rewrite": self.rewrite,
                 "locations": [ l.location for l in self.locations_to_rewrite ] }


class SymbolMap:
    def __init__(self):
        self.symbols = {}
        self.records = {}

    def _symbol_for(self, name, loc):
        if not self.symbols.get(name):
            newsym = Symbol(name)
            self.symbols[name] = newsym
            if loc.kind == "RecordDecl":
                # XXX: Should take care of namespace.
                self.records[loc.name] = newsym
        return self.symbols[name]

    def _add_from_location(self, loc):
        for name in loc.symbols:
            self._symbol_for(name, loc).add_location(loc)

    def add_from_json(self, root):
        for loc in root["locations"]:
            if loc:
                self._add_from_location(Location(loc))

    def find(self, name):
        return self.symbols.get(name)

    def mark_children(self):
        for name, symbol in self.symbols.items():
            if symbol.parent:
                parent = self.records[symbol.parent]
                if parent.rewrite == "export":
                    if symbol.inlined:
                        symbol.mark_rewrite_as("inline")
                    elif symbol.rewrite == "export":
                        symbol.mark_rewrite_as(None)


def to_before_exported(symbol):
    if symbol[0] == "_":
        return symbol[1:]
    return symbol


if __file__ == sys.argv[0]:
    parser = OptionParser()
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Print status messages to stdout")
    parser.add_option("-f", "--filter", dest="filter",
                      help="FILE contains the list of printing symbols", metavar="FILE")
    (options, args) = parser.parse_args()

    location_files = args
    symbol_map = SymbolMap()

    for file_index in range(0, len(location_files)):
        filename = location_files[file_index]
        file = open(filename)
        symbol_map.add_from_json(json.load(file))
        file.close()

    if options.verbose:
        sys.stderr.write("Loaded symbols (%d/%d): %d\n" % (file_index+1, len(location_files), len(symbol_map.symbols)))

    if options.filter:
        exported_symbols = [ to_before_exported(s.strip()) for s in open(options.filter).readlines() ]
        for name in exported_symbols:
            symbol_map.find(name).mark_rewrite_as("export")
    else:
        for name, symbol in symbol_map.symbols.items():
            symbol.mark_rewrite_as("noop")

    symbol_map.mark_children()

    print """{ "symbols": ["""
    for name, symbol in symbol_map.symbols.items():
        if symbol.rewrite:
            print json.dumps(symbol.to_json()), ","
    print """null ]}"""
