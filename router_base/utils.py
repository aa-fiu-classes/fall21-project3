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

import sys
from .headers import EtherHeader, IpHeader, ArpHeader, IcmpHeader, Stack

def checksum(data):
    sum = 0
    for offset in range(0, len(data), 2):
        val = int.from_bytes(data[offset:offset + 2], byteorder='little')
        value = (val & 0xff) << 8 | (val & 0xff00) >> 8
        sum = sum + value

    while sum > 0xffff:
        sum = (sum >> 16) + (sum & 0xFFFF)
    sum = ~sum & 0xffff
    if sum:
        return sum
    else:
        return 0xffff

    
# prints all headers, starting from eth
def print_hdrs(buf, file=sys.stdout):
    hdrClass = EtherHeader
    offset = 0

    while offset < len(buf):
        hdr = hdrClass()
        offset = offset + hdr.decode(buf[offset:])
        print(hdr, file=file)
        try:
            nextLevel = Stack[hdr.__class__]
        except KeyError:
            break
        try:
            hdrClass = nextLevel[hdr.next_level()]
        except KeyError:
            print("Unrecognized payload type [%d] for %s" % (hdr.next_level(), hdrClass.__name__), file=file)
            break
