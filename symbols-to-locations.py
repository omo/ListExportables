#!/usr/bin/env python

import sys
import json

symbols_file = sys.argv[1]
location_files = sys.argv[2:]

class Location:
    def __init__(self, location_dict):
        self.position = location_dict["file"]
        self.symbols = location_dict["symbols"]
        
    def __eq__(self, other):
        return self.position == other.position and self.symbols == other.symbols


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
        

location_map = LocationMap()

for file_index in range(0, len(location_files)):
    filename = location_files[file_index]
    file = open(filename)
    location_map.add_from_json(json.load(file))
    file.close()
    print "Loaded symbols (%d/%d): %d" % (file_index, len(location_files), len(location_map.symbol_to_loc))

if False:
    for k, v in location_map.symbol_to_loc.items():
        print k

exported_symbols = [ to_before_exported(s.strip()) for s in open(symbols_file).readlines() ]
print "Exported symbols: %d" % len(exported_symbols)

if True:
    for symbol in exported_symbols:
        locations = location_map.find_locations(symbol)
        if not locations:
            sys.stderr.write("Location is not found: %s\n" % symbol)
#        if locations:
#            sys.stderr.write("Found location: %s\n" % symbol)
     


    
