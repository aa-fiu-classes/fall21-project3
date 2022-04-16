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

from router_base import ArpCacheBase
from router_base.headers import *
import time

MAX_SENT_TIME = 5

# ArpCache and ArpCacheBase define an ARP cache with ARP request queue and ARP cache entries.
# The ARP cache entries hold IP->MAC mappings and are timed out every SR_ARPCACHE_TO seconds.

class ArpCache(ArpCacheBase):

    def __init__(self, router):
        super().__init__()
        self.router = router

    def handleIncomingArpReply(self, arpHeader): # add more params as needed
        '''
        IMPLEMENT THIS METHOD

        YOU NEED TO CALL THIS METHOD FROM YOUR ROUTER IMPLEMENTATION

        The ARP reply processing code should move entries from the ARP request
        queue to the ARP cache:

            # Lookup request using the decoded arpHeader

            # When servicing an arp reply that gives us an IP->MAC mapping
            req = cache.insertArpEntry(ip, mac)

            if req:
                send all packets on the req->packets linked list
                cache.removeRequest(req)
        '''

        pass

    def resendOrRemoveQueuedRequest(self, req):
        '''
        IMPLEMENT THIS METHOD

        This method is automatically called every second

        This method should handle sending ARP requests if necessary.
        The high-level logic:

            if now - req.timeSent > 1 # seconds
                if req.nTimesSent >= 5:
                    send icmp host unreachable to source addr of all pkts waiting
                      on this request
                    cache.removeRequest(req)
                else:
                    send arp request
                    req.timeSent = time.time()
                    req.nTimesSent++
        '''

        pass

    def periodicCheckArpRequestsAndCacheEntries(self):
        '''
        This method is called every second. For each request sent out,
        it calls out a method you need to implement to check whether
        to re-send or remove the request, and then cleans up no longer valid
        entries in the ARP cache.
        '''
        for request in self.arpRequests:
            self.resendOrRemoveQueuedRequest(request)

        entriesToRemove = []
        for entry in self.cacheEntries:
            if not entry.isValid:
                entriesToRemove.append(entry)

        for entry in entriesToRemove:
            self.cacheEntries.remove(entry)
