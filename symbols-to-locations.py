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
    def symbolType(self):
        return self.dict["type"]
        
    @property
    def location(self):
        return self.dict["location"]

    @property
    def location_with_definition(self):
        return self.dict["location"] + [ self.definition ]

    @property
    def symbols(self):
        return self.dict["symbols"]

    @property
    def definition(self):
        return self.dict["definition"]

    def __eq__(self, other):
        return self.location == other.location and self.symbols == other.symbols


class LocationMap:
    def __init__(self):
        self.symbol_to_loc = {}

    def _location_list_for(self, sym):
        if not self.symbol_to_loc.get(sym):
            self.symbol_to_loc[sym] = []
        return self.symbol_to_loc[sym]

    def add(self, loc):
        for s in loc.symbols:
            locations = self._location_list_for(s)
            if not locations.count(loc):
                locations.append(loc)

    def add_from_json(self, root):
        for loc in root["locations"]:
            if loc:
                self.add(Location(loc))

    def find_locations(self, symbol):
        return self.symbol_to_loc.get(symbol)


def to_before_exported(symbol):
    if symbol[0] == "_":
        return symbol[1:]
    return symbol

def print_symbol_to_location(sym, locs):
    print json.dumps({"symbol": sym, "type": locs[0].symbolType,
                      "locations": [ l.location_with_definition for l in locs ]}), ","

if __file__ == sys.argv[0]:
    parser = OptionParser()
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Print status messages to stdout")
    parser.add_option("-f", "--filter", dest="filter",
                      help="FILE contains the list of printing symbols", metavar="FILE")
    parser.add_option("-e", "--all",
                      action="store_true", dest="all", default=False,
                      help="Print status messages to stdout")
    (options, args) = parser.parse_args()

    location_files = args
    location_map = LocationMap()

    for file_index in range(0, len(location_files)):
        filename = location_files[file_index]
        file = open(filename)
        location_map.add_from_json(json.load(file))
        file.close()

    if options.verbose:
        sys.stderr.write("Loaded symbols (%d/%d): %d\n" % (file_index+1, len(location_files), len(location_map.symbol_to_loc)))

    print """{ "symbols": ["""
    if options.filter:
        exported_symbols = [ to_before_exported(s.strip()) for s in open(options.filter).readlines() ]
        for symbol in exported_symbols:
            locations = location_map.find_locations(symbol)
            if not locations:
                sys.stderr.write("Location is not found: %s\n" % symbol)
            else:
                print_symbol_to_location(symbol, locations)
    else:
        for sym, locs in location_map.symbol_to_loc.items():
            print_symbol_to_location(sym, locs)
    print """null ]}"""
