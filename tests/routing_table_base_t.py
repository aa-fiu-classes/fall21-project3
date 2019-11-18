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
from router_base import routing_table_base

class TestRoutingTableBase(unittest.TestCase):

    def test_entry(self):
        """Test of routing table entry"""

        entry = routing_table_base.RoutingTableEntry("1.1.1.0", "0.0.0.0", "255.255.255.0", "eth0")
        self.assertEqual(str(entry), "1.1.1.0            255.255.255.0      0.0.0.0            eth0")

        entry.mask = 0
        self.assertEqual(str(entry), "1.1.1.0            0.0.0.0            0.0.0.0            eth0")

        entry.dest = "0.0.0.0"
        entry.gw = "1.1.1.1"
        entry.ifName = "eth1"
        self.assertEqual(str(entry), "0.0.0.0            0.0.0.0            1.1.1.1            eth1")
        
    def test_table_base(self):
        """Basic test of the routing table"""

        table = routing_table_base.RoutingTableBase()
        table.load("tests/RTABLE")
        self.assertEqual(len(table.entries), 3)

        self.assertEqual(str(table), """Destination        Mask               Gateway            Iface
0.0.0.0            0.0.0.0            10.0.1.100         sw0-eth3
192.168.2.2        255.255.255.0      192.168.2.2        sw0-eth1
172.64.3.10        255.255.0.0        172.64.3.10        sw0-eth2
""")

if __name__ == '__main__':
    unittest.main()
