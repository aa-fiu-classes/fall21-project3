# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-
# Copyright 2019 Alex Afanasyev
#
# This program is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.

from .ip_address import IpAddress
import io
from functools import partial

class RoutingTableEntry:
    # dest
    # gw
    # mask
    # ifName
  
    def __init__(self, dest, gw, mask, ifName):
        self.dest = dest
        self.gw = gw
        self.mask = mask
        self.ifName = ifName

    def __get_ip(name, self):
        return getattr(self, "__%s" % name)
    
    def __set_ip(name, self, value):
        setattr(self, "__%s" % name, IpAddress(value))
    
    dest = property(partial(__get_ip, "dest"), partial(__set_ip, "dest"))
    gw   = property(partial(__get_ip, "gw"),   partial(__set_ip, "gw"))
    mask = property(partial(__get_ip, "mask"), partial(__set_ip, "mask"))

    def __str__(self):
        return f"{str(self.dest):18} {str(self.mask):18} {str(self.gw):18} {self.ifName}"
    
class RoutingTableBase:

    def __init__(self):
        self.entries = []
    
    def load(self, file):
        """Load routing table from file"""

        with open(file, "rt") as f:
            for line in f:
                dest, gw, mask, iface = line.split()
                entry = RoutingTableEntry(dest, gw, mask, iface)
                self.addEntry(entry)

    def addEntry(self, entry):
        if not isinstance(entry, RoutingTableEntry):
            raise RuntimeError(".addEntry method expects RoutingTableEntry as the only parameter")
        self.entries.append(entry)

    def __str__(self):
        f = io.StringIO()
        print(f"{'Destination':18} {'Mask':18} {'Gateway':18} Iface", file=f)
        for entry in self.entries:
            print(entry, file=f)
        return f.getvalue()
