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

import Ice
import os
import logging
import sys
from .interface import Interface
from .ip_address import IpAddress

log = logging.getLogger("riddikulus.simple_router_base")

class SimpleRouterBase:
    def __init__(self, routingTable, arpCache):
        self.routingTable = routingTable
        self.arpCache = arpCache
        self.ifaces = []
        self.ifNameToIpMap = {}

    def sendPacket(self, packet, outIface):
        self.pox.begin_sendPacket(packet, outIface)

    #
    # Load routing table information from \p rtConfig file
    #
    def loadRoutingTable(self, rtConfig):
        return self.routingTable.load(rtConfig)

    #
    # Load local interface configuration
    #
    def loadIfconfig(self, ifconfig):
        with open(ifconfig, "rt") as f:
            for cnt, line in enumerate(f):
                items = line.split()
                if len(items) != 2:
                    raise RuntimeError("Error on line %d: expected two values (iface, ip) separated by space, got [%s]" % (cnt, line))
                iface, ip = items

                try:
                    self.ifNameToIpMap[iface] = IpAddress(ip)
                except:
                    raise RuntimeError("Invalid IP address `%s` for interface `%s`" % (ipStr, iface));

    #
    # Get routing table
    #
    def getRoutingTable(self):
        return self.routingTable

    #
    # Get ARP table
    #
    def getArp(self):
        return self.arpCache
    
    #
    # Print router interfaces
    #
    def printIfaces(self, file):
        if len(self.ifaces) == 0:
            file.write( " Interface list empty \n")

        for iface in self.ifaces:
                file.write("%s\n" % iface)

    #
    # Reset ARP cache and interface list (e.g., when mininet restarted)
    #
    def reset(self, ports):
        print("Resetting SimpleRouter with %d ports" % len(ports), file=sys.stderr)
        self.arpCache.reset()

        self.ifaces = []

        for iface in ports:
            try:
                ip = self.ifNameToIpMap[iface.name]
            except KeyError:
                print("IP_CONFIG missing information about interface `%s`. Skipping it" % iface.name, file=sys.stderr)
                continue
            
            self.ifaces.append(Interface(iface.name, iface.mac, ip))

        self.printIfaces(file=sys.stderr)

    #
    # Find interface based on interface's IP address
    #
    def findIfaceByIp(self, ip):
        for iface in self.ifaces:
            if iface.ip == ip:
                return iface
        return None

    #
    # Find interface based on interface's MAC address
    #
    def findIfaceByMac(self, mac):
        for iface in self.ifaces:
            if iface.addr == mac:
                return iface
        return None

    #
    # Find interface based on interface's name
    #
    def findIfaceByName(self, ifName):
        for iface in self.ifaces:
            if iface.name == ifName:
                return iface
        return None
