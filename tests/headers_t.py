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
from router_base import headers

class TestHeaders(unittest.TestCase):
    EtherArpHdr = b'\xf8\xe9Nt\xde:\xf0\x18\x98\x96\xe3\x18\x08\x06\x00\x01\x08\x00\x06\x04\x00\x01\xf0\x18\x98\x96\xe3\x18\xc0\xa8d\x9c\xf8\xe9Nt\xde:\xc0\xa8d\x97'

    EtherIpIcmpHddr = b'\xf0\x18\x98\x96\xe3\x18\x1c\xf2\x9a\xa0(!\x08\x00E\x00\x00T\xa4o\x00\x005\x01\xb9\xf3\x01\x01\x01\x01\xc0\xa8d\x9c\x00\x00i\x07\xc5Z\x00\x02]\xd1\x98\x7f\x00\x01\xf0F\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01234567'

    # EtherHeader, IpHeader, ArpHeader, IcmpHeader
    def test_ether(self):
        """Check EtherHeader"""

        h1 = headers.EtherHeader(TestHeaders.EtherArpHdr)

        h2 = headers.EtherHeader()
        offset = h2.decode(TestHeaders.EtherArpHdr)
        self.assertEqual(offset, 14)

        self.assertEqual(str(h1), str(h2))
        self.assertEqual(str(h1.dhost), "f8:e9:4e:74:de:3a")
        self.assertEqual(str(h1.shost), "f0:18:98:96:e3:18")
        self.assertEqual(h1.type, 2054)

        h3 = headers.EtherHeader(shost="f0:18:98:96:E3:18", dhost="f8:e9:4e:74:de:3a", type=2054)
        self.assertEqual(str(h1), str(h3))
        self.assertEqual(len(h3.encode()), 14)
        self.assertEqual(h3.encode(), TestHeaders.EtherArpHdr[:14])

        h3.dhost = "ff:ff:ff:ff:ff:ff"
        h3.shost = "00:00:00:00:00:00"
        h4 = headers.EtherHeader(h3.encode())
        self.assertEqual(str(h4.shost), str(h3.shost))
        self.assertEqual(str(h4.dhost), str(h3.dhost))

    def test_ip(self):
        """Check IpHeader"""

        h1 = headers.IpHeader(TestHeaders.EtherIpIcmpHddr[14:])

        h2 = headers.IpHeader()
        offset = h2.decode(TestHeaders.EtherIpIcmpHddr[14:])
        self.assertEqual(offset, 20)

        self.assertEqual(str(h1), str(h2))
        self.assertEqual(str(h1), "IpHeader: v=4 hl=5 tos=0 len=84 id=42095 off=0 ttl=53 p=1 sum=47603 src=1.1.1.1 dst=192.168.100.156")
        self.assertEqual(h1.sum, 47603)
        self.assertEqual(h1.ttl, 53)
        self.assertEqual(str(h1.src), "1.1.1.1")

        h3 = headers.IpHeader(hl=5, tos=0, len=84, id=42095, off=0, ttl=53, p=1, sum=47603, src='1.1.1.1', dst='192.168.100.156')
        self.assertEqual(str(h1), str(h3))
        self.assertEqual(len(h3.encode()), 20)
        self.assertEqual(h3.encode(), TestHeaders.EtherIpIcmpHddr[14:14+20])

        h3.src = '2.2.2.2'
        h3.dst = '255.255.255.255'
        h4 = headers.IpHeader(h3.encode())
        self.assertEqual(str(h3.src), str(h4.src))
        self.assertEqual(str(h3.dst), str(h4.dst))

    def test_arp(self):
        """Check ArpHeader"""

        h1 = headers.ArpHeader(TestHeaders.EtherArpHdr[14:])

        h2 = headers.ArpHeader()
        offset = h2.decode(TestHeaders.EtherArpHdr[14:])
        self.assertEqual(offset, 28)

        self.assertEqual(str(h1), str(h2))
        self.assertEqual(str(h1), "ArpHeader: hrd=1 pro=2048 hln=6 pln=4 op=1 sha=f0:18:98:96:e3:18 sip=192.168.100.156 tha=f8:e9:4e:74:de:3a tip=192.168.100.151")
        self.assertEqual(h1.hln, 6)
        self.assertEqual(h1.pln, 4)
        self.assertEqual(h1.op, 1)

        h3 = headers.ArpHeader(hln=6, pln=4, op=1, sha='f0:18:98:96:e3:18', sip='192.168.100.156', tha='f8:e9:4e:74:de:3a', tip='192.168.100.151')
        self.assertEqual(str(h1), str(h3))
        self.assertEqual(len(h3.encode()), 28)
        self.assertEqual(h3.encode(), TestHeaders.EtherArpHdr[14:14+28])

        h3.sha = "ff:ff:ff:ff:ff:ff"
        h3.tha = "00:00:00:00:00:00"
        h3.sip = '2.2.2.2'
        h3.tip = '255.255.255.255'
        h4 = headers.ArpHeader(h3.encode())
        self.assertEqual(str(h3.sha), str(h4.sha))
        self.assertEqual(str(h3.tha), str(h4.tha))
        self.assertEqual(str(h4.sip), str(h3.sip))
        self.assertEqual(str(h4.tip), str(h3.tip))

    def test_icmp(self):
        """Check IcmpHeader"""

        h1 = headers.IcmpHeader(TestHeaders.EtherIpIcmpHddr[34:])

        h2 = headers.IcmpHeader()
        offset = h2.decode(TestHeaders.EtherIpIcmpHddr[34:])
        self.assertEqual(offset, 64)

        self.assertEqual(str(h1), str(h2))
        self.assertEqual(str(h1), r"""IcmpHeader: type=0 code=0 sum=26887 id=50522 seqNum=2 data=b']\xd1\x98\x7f\x00\x01\xf0F\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01234567'""")
        self.assertEqual(h1.type, 0)
        self.assertEqual(h1.code, 0)
        self.assertEqual(h1.sum, 26887)
        self.assertEqual(h1.id, 50522)
        self.assertEqual(h1.seqNum, 2)
        self.assertEqual(h1.data, b']\xd1\x98\x7f\x00\x01\xf0F\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01234567')
        self.assertEqual(len(h1.data), 56)

        h3 = headers.IcmpHeader(type=0, code=0, sum=26887, id=50522, seqNum=2, data=b']\xd1\x98\x7f\x00\x01\xf0F\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./01234567')
        self.assertEqual(len(h3.encode()), 64)
        self.assertEqual(str(h1), str(h3))
        self.assertEqual(h3.encode(), TestHeaders.EtherIpIcmpHddr[34:34+64])

if __name__ == '__main__':
    unittest.main()
