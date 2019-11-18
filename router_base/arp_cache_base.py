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

import time
import io
import threading
from .mac_address import MacAddress
from .ip_address import IpAddress

SR_ARPCACHE_TO = 30

class ArpRequest:
    def __init__(self, ip, iface):
      self.ip = ip
      self.iface = iface
      self.nTimesSent = 0
      self.packets = []

      # Last time this ARP request was sent. You should update this. If
      # the ARP request was never sent, self.timeSent == None
      self.timeSent = time.time()

class ArpEntry:
    def __init__(self, mac, ip):
        self.mac = MacAddress(mac)
        self.ip = IpAddress(ip)
        self.timeAdded = time.time()
        self.isValid = True
        
class ArpCacheBase:
    def __init__(self):
        self.cacheEntries = []
        self.arpRequests = []  

        self.shouldStop = False

        self.mutex = threading.RLock()
        self.tickerThread = threading.Thread(target=self.__ticker)
        self.tickerThread.start()

    def stop(self):
        self.shouldStop = True
        self.tickerThread.join()

    def reset(self):
        self.mutex.acquire()
        self.cacheEntries = []
        self.arpRequests = []  
        self.mutex.release()
        
    def lookup(self, ip):
        '''
        Checks if an IP->MAC mapping is in the cache. IP is in network byte order.
        You must free the returned structure if it is not NULL.
        '''

        self.mutex.acquire()

        found = None
        for entry in self.cacheEntries:
            if entry.isValid and entry.ip == ip:
                found = entry
                break

        self.mutex.release()

        return found
    
    def queueRequest(self, ip, packet, iface):
        '''
        Adds an ARP request to the ARP request queue. If the request is already on
        the queue, adds the packet to the linked list of packets for this sr_arpreq
        that corresponds to this ARP request. The packet argument should not be
        freed by the caller.
        
        A pointer to the ARP request is returned; it should not be freed. The caller
        can remove the ARP request from the queue by calling sr_arpreq_destroy.

        :returns True if request for this IP already existed
        '''

        self.mutex.acquire()

        queuedRequest = None
        requestExisted = False
        for request in self.arpRequests:
            if request.ip == ip:
                queuedRequest = request
                break
        if queuedRequest is None:
            queuedRequest = ArpRequest(ip, iface)
            self.arpRequests.append(queuedRequest)
        else:
            requestExisted = True

        queuedRequest.packets.append(packet)
        
        self.mutex.release()
        return requestExisted
    
    def removeRequest(self, arpRequest):
        '''
        Frees all memory associated with this arp request entry. If this arp request
        entry is on the arp request queue, it is removed from the queue.
        '''

        self.mutex.acquire()
        try:
            self.arpRequests.remove(arpRequest)
        except:
            pass

        self.mutex.release()

    def insertArpEntry(self, mac, ip):
        '''
        This method performs two functions:
        
        1) Looks up this IP in the request queue. If it is found, returns a pointer
           to the ArpRequest with this IP. Otherwise, returns None.
        2) Inserts this IP to MAC mapping in the cache, and marks it valid.
        '''

        self.mutex.acquire()

        entry = ArpEntry(mac, ip)
        self.cacheEntries.append(entry)

        foundRequest = None
        for request in self.arpRequests:
            if request.ip == ip:
                foundRequest = request
                break
        
        self.mutex.release()

        return foundRequest
        
    def clear(self):
        '''
        Clear all entries in ARP cache and requests.
        '''
        self.mutex.acquire()
        self.cacheEntries = []
        self.arpRequests = []
        self.mutex.release()

    def __str__(self):
        self.mutex.acquire()
        f = io.StringIO()
        print(f"{'MAC':20} {'IP':18} {'AGE':20}  {'Is Valid'}", file=f)
        print("----------------------------------------------------------------------", file=f)

        now = time.time()
        for entry in self.cacheEntries:
            print(f"{str(entry.mac):20} {str(entry.ip):18} {now - entry.timeAdded:12.2f} seconds  {entry.isValid}", file=f)
      
        self.mutex.release()

        return f.getvalue()
      
    def __ticker(self):
        '''
        Thread which sweeps through the cache and invalidates entries that were added
        more than SR_ARPCACHE_TO seconds ago.
        '''

        while not self.shouldStop:
            time.sleep(1)

            self.mutex.acquire()

            now = time.time()
            for entry in self.cacheEntries:
                if entry.isValid and (now - entry.timeAdded > SR_ARPCACHE_TO):
                    entry.isValid = False

            try:
                # calling the "implementation" method
                self.periodicCheckArpRequestsAndCacheEntries()
            finally:
                self.mutex.release()
