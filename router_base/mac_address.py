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

import re
import struct

class MacAddress:
    def __init__(self, addr):
        if isinstance(addr, MacAddress):
            self.addr = addr.addr
        elif isinstance(addr, bytes):
            if len(addr) != 6:
                raise RuntimeError("Invalid mac address length")
            self.addr = addr
        elif isinstance(addr, str):
            comps = re.split('[-:]', addr)
            if len(comps) != 6:
                raise RuntimeError("Invalid MAC address: %s" % addr)
            self.addr = struct.pack("!cccccc", *[bytes([int(i, 16)]) for i in comps])
        else:
            raise RuntimeError("Incompatible input: %s" % addr)

    def __str__(self):
        return ':'.join([f"{i:0{2}x}" for i in self.addr])

    def __bytes__(self):
        return self.addr
