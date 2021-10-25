#!/usr/bin/env python3
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

from router_base import SimpleRouterBase, PoxConnectorApp

from ridikkulus_routing_table import RoutingTable
from ridikkulus_arp_cache import ArpCache

from router_base.headers import *
from router_base.mac_address import MacAddress
from router_base.ip_address import IpAddress
from router_base.interface import Interface
from router_base.utils import checksum, print_hdrs

import sys

class SimpleRouter(SimpleRouterBase):

    #
    # IMPLEMENT THIS METHOD TO HANDLE THE RECEIVED PACKETS
    #
    # This method is called each time the router receives a packet on
    # the interface.  The packet buffer \p origPacket and the receiving
    # interface \p inIface are passed in as parameters. The packet is
    # complete with ethernet headers.
    #
    def handlePacket(self, origPacket, inIface):
        print("Got packet of size %d on interface %s" % (len(origPacket), inIface), file=sys.stderr)

        iface = self.findIfaceByName(inIface)
        if not iface:
            print("Received packet, but interface is unknown, ignoring", file=sys.stderr)
            return

        # all incoming packets are guaranteed to be Ethernet, so unconditionally process them as Ethernet
        self.processEther(origPacket, iface)

    def processEther(self, etherPacket, iface):
        '''
        SUGGESTED IMPLEMENTATION LOGIC
        You are free to implement this method and relevant calling methods in other methods
        or ignore it and implement in a completely different way

        \p etherPacket packet buffer that starts with the Ethernet header
        \p iface instance of Interface class (it has .name, .mac, and .ip members)
        '''

        etherHeader = EtherHeader()
        offset = etherHeader.decode(etherPacket)
        restOfPacket = etherPacket[offset:]

        # Study fields available in each header in router_base/headers.py.
        # All fields there follow the correspodning specifications, so you may
        # need to check those, if any question

        if etherHeader.type == 0x0806:
            self.processArp(self, restOfPacket, etherHeader, iface)
        elif etherHeader.type == 0x0800:
            self.processIp(self, restOfPacket, iface)
        else
            # ignore packets that neither ARP nor IP
            pass

    def processArp(self, arpPacket, origEtherHeader, iface):
        '''
        SUGGESTED IMPLEMENTATION LOGIC
        You are free to implement this method and relevant calling methods in other methods
        or ignore it and implement in a completely different way

        \p etherPacket packet buffer that starts with the Ethernet header
        \p origEtherHeader decoded ethernet header
        \p iface instance of Interface class (it has .name, .mac, and .ip members)

        What needs to be implemented here:
        - decode ARP header
        - check if ARP is request (somebody is asking) or reply (sombody is replying to your request)
        - if request, need to check if somebody asking about YOUR IP.  For this, extract IP
          address from the ARP request and call   self.findIfaceByIp() method to find a local interface
          that corresponds to this IP.  If no IP found, then request is not for you and should be ignored.
        - if it is response, then you should decode and call self.arpCache.handleIncomingArpReply()
        '''
        pass

    def processIp(self, ipPacket, iface):
        '''
        SUGGESTED IMPLEMENTATION LOGIC
        You are free to implement this method and relevant calling methods in other methods
        or ignore it and implement in a completely different way

        \p iface instance of Interface class (it has .name, .mac, and .ip members)

        What needs to be implemented here:
        - decode IP header
        - check if IP packet to ONE OF ROUTER'S IP addresses (can be do any interface that the router
          has and all of such packets should be treated equally).  You can use self.findIfaceByIp() method.
          If no interface found, then this packet is for someone else and you should call self.processIpToForward()
        - If it is for the router, then call self.processIpToSelf
        '''
        pass


    def processIpToSelf(self, ipPacket, origIpHeader, iface):
        '''
        SUGGESTED IMPLEMENTATION LOGIC
        You are free to implement this method and relevant calling methods in other methods
        or ignore it and implement in a completely different way

        \p iface instance of Interface class (it has .name, .mac, and .ip members)

        In our project, one can either send ICMP packets (ping) to the router or it will be
        a UDP packet to a random port when traceroute is used.  Therefore, you need to decode
        ipPacket and determine which is which, ignoring any other types of packets (e.g., TCP).
        '''
        pass

    def processIcmp(self, icmpPacket, origIpHeader, iface):
        '''
        SUGGESTED IMPLEMENTATION LOGIC
        You are free to implement this method and relevant calling methods in other methods
        or ignore it and implement in a completely different way

        \p iface instance of Interface class (it has .name, .mac, and .ip members)

        Decode ICMP packet and process ICMP pings (=send reply). All other incoming ICMP packets can be ignored.
        '''
        pass

    def processUdp(self, udpPacket, origIpHeader, iface):
        '''
        SUGGESTED IMPLEMENTATION LOGIC
        You are free to implement this method and relevant calling methods in other methods
        or ignore it and implement in a completely different way

        \p iface instance of Interface class (it has .name, .mac, and .ip members)

        You don't actually decode udpPacket, but rather just implement ICMP destination port unreachable response.
        '''
        pass

    def processIpToForward(self, ipPacket, origIpHeader, iface):
        '''
        SUGGESTED IMPLEMENTATION LOGIC
        You are free to implement this method and relevant calling methods in other methods
        or ignore it and implement in a completely different way

        \p iface instance of Interface class (it has .name, .mac, and .ip members)

        This is the starting point for forwarding a packet according to the routing table rules.
        Here you first need to lookup a routing table (routing table is configured automatically,
        you don't need to do anything, except looking it up + implementation of the longest prefix
        match logic).

        First, check if checksum is valid and TTL is enough to forward.  You need to report errors
        (properly respond with ICMP correct) to the source: need to create new ICMP header, new IP header,
        new Ethernet header, etc.  Don't forget to calculate proper checksums for ICMP and IP headers.

        entry = self.routingTable.lookup()

        The entry has  .dest, .gw, .mask, and .ifName fields. For forwarding, .ifName and .gw will be relevant.

        Assumptions here:
        - if .gw is 0.0.0.0  (you can check   entry.gw == 0), then the packet can be directly forwarded
          to the interface (i.e., the host is directly adjacent).   In this case, you need to lookup
          ARP cache for the origIpHeader.dst (self.arpCache.lookup()), if you have an existing entry,
          then use its info (arpEntry.mac for the new EthernetHeader's destination mac), and then create
          new Ethernet header, reduce TTL, recalculated checksum, create full packet and forward it.

          If arp cache entry doesn't exist, you need to create ARP request, send ARP request, and then
          queue the request: self.arpCache.queueRequest(ip, ipPacket, interfaceLookedUpByRoutingTable).
          Whenever response comes, you will be sending the packet(s) from inside of ridikkulus_arp_cache.py:handleIncomingArpReply

        - if .gw is anything but 0.0.0.0 the process is exactly the same as above, but you need to use
          entry.gw address instead of origIpHeader.dst for ARP cache lookup.  IP header's destination IP
          stays original, .gw only used to lookup MAC address of the gateway!

        '''
        pass

    #
    # USE THIS METHOD TO SEND PACKETS OUT
    #
    # Call this method to send packet \p packet from the router on interface \p outIface
    #
    def sendPacket(self, packet, outIface):
        super().sendPacket(packet, outIface)

    ##############################################################################
    ######################### DO NOT EDIT THE REST ###############################
    ##############################################################################

    def __init__(self):
        super().__init__(RoutingTable(), ArpCache(self))

if __name__ == '__main__':
    rtr = SimpleRouter()
    app = PoxConnectorApp(rtr)
    app.main(sys.argv, "router.config")
