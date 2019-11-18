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

MAX_SENT_TIME = 5

# ArpCache and ArpCacheBase define an ARP cache with ARP request queue and ARP cache entries.
# The ARP cache entries hold IP->MAC mappings and are timed out every SR_ARPCACHE_TO seconds.

class ArpCache(ArpCacheBase):

    def __init__(self, router):
        super().__init__()
        self.router = router

    def handleArpRequest(self): # add more params as needed
        '''
        IMPLEMENT THIS METHOD

        This method should handle sending ARP requests if necessary.
        The high-level logic:

            if now - req->timeSent > seconds(1)
                if req->nTimesSent >= 5:
                    send icmp host unreachable to source addr of all pkts waiting
                      on this request
                    cache.removeRequest(req)
                else:
                    send arp request
                    req->timeSent = now
                    req->nTimesSent++
        '''

        pass

    def handleArpReply(self): # add more params as needed
        '''
        IMPLEMENT THIS METHOD

        The ARP reply processing code should move entries from the ARP request
        queue to the ARP cache:

            # When servicing an arp reply that gives us an IP->MAC mapping
            req = cache.insertArpEntry(ip, mac)

            if req != nullptr:
                send all packets on the req->packets linked list
                cache.removeRequest(req)
        '''

        pass

    def periodicCheckArpRequestsAndCacheEntries(self):
        '''
        IMPLEMENT THIS METHOD

        This method gets called every second. For each request sent out,
        you should keep checking whether to resend a request or remove it.

        Your implementation should follow the following logic

            for each request in queued requests:
                handleRequest(request)

            for each cache entry in entries:
                if not entry->isValid
                    record entry for removal
            remove all entries marked for removal
        '''
        pass
