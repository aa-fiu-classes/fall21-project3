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

import unittest
import io
from router_base import utils, headers

class TestUtils(unittest.TestCase):
    Files = {
        "raw-arp-request.bin": {
            'sum': -1,
            'str': r"""EtherHeader: dhost=f8:e9:4e:74:de:3a shost=f0:18:98:96:e3:18 type=2054
ArpHeader: hrd=1 pro=2048 hln=6 pln=4 op=1 sha=f0:18:98:96:e3:18 sip=192.168.100.156 tha=f8:e9:4e:74:de:3a tip=192.168.100.151
"""
        },
        "raw-icmp-reply.bin": {
            'sum': 47603,
            'str': r"""EtherHeader: dhost=f0:18:98:96:e3:18 shost=1c:f2:9a:a0:28:21 type=2048
IpHeader: v=4 hl=5 tos=0 len=84 id=42095 off=0 ttl=53 p=1 sum=47603 src=1.1.1.1 dst=192.168.100.156
IcmpHeader: type=0 code=0 sum=26887 id=50522 seqNum=2 data=b']\xd1\x98\x7f\x00\x01\xf0F\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01234567'
"""
        },
        "raw-icmp-request.bin": {
            'sum': 10909,
            'str': r"""EtherHeader: dhost=1c:f2:9a:a0:28:21 shost=f0:18:98:96:e3:18 type=2048
IpHeader: v=4 hl=5 tos=0 len=84 id=10438 off=0 ttl=64 p=1 sum=10909 src=192.168.100.156 dst=1.1.1.1
IcmpHeader: type=8 code=0 sum=24839 id=50522 seqNum=2 data=b']\xd1\x98\x7f\x00\x01\xf0F\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01234567'
"""
        },
        "raw-udp.bin": {
            'sum': 21876,
            'str': r"""EtherHeader: dhost=ff:ff:ff:ff:ff:ff shost=02:ff:60:14:fa:0a type=2048
IpHeader: v=4 hl=5 tos=0 len=49 id=55945 off=0 ttl=64 p=17 sum=21876 src=192.168.100.110 dst=192.168.100.255
Unrecognized payload type [17] for IpHeader
"""
        },
    }

    def test_checksum(self):
        """Check IP hecksum calculation"""
        for fname, testData in TestUtils.Files.items():
            if testData['sum'] < 0:
                continue
            pkt = open("tests/raw-packets/%s" % fname, "rb").read()
            sum = utils.checksum(pkt[14:14+20]) # look IP header only
            self.assertEqual(sum, 65535)

            hdr = headers.IpHeader(pkt[14:14+20])
            hdr.sum = 0
            sum = utils.checksum(hdr.encode())
            self.assertEqual(sum, testData['sum'])

    def test_print_hdrs(self):
        """Check packet header printing"""
        for fname, testData in TestUtils.Files.items():
            # print(fname)
            pkt = open("tests/raw-packets/%s" % fname, "rb").read()
            f = io.StringIO()
            utils.print_hdrs(pkt, file=f)
            # print(f.getvalue())
            self.assertEqual(f.getvalue(), testData['str'])

if __name__ == '__main__':
    unittest.main()
