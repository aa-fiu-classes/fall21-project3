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
import sys
import logging
import threading
import time

log = logging.getLogger("riddikulus.connector")

slice_dir = Ice.getSliceDir()
if not slice_dir:
    log.error(sys.argv[0] + ': Slice directory not found.')
    sys.exit(1)

Ice.loadSlice("", ["-I%s" % slice_dir, "%s/pox.ice" % os.path.dirname(os.path.realpath(__file__))])
import pox

class PacketHandler(pox.PacketHandler):
    def __init__(self, router):
        self.router = router

    def handlePacket(self, packet, inIface, current):
      self.router.handlePacket(packet, inIface)

    def resetRouter(self, ports, current):
      self.router.reset(ports)

class Tester(pox.Tester):
    def __init__(self, router):
        self.router = router

    def getArp(self, current):
        return str(self.router.getArp())

    def getRoutingTable(self, current):
        return str(self.router.getRoutingTable())

class PoxConnectorApp(Ice.Application):
  def __init__(self, simpleRouter):
    super().__init__()
    self.router = simpleRouter
  
  def run(self, argv):
    rtFile = self.communicator().getProperties().getPropertyWithDefault("RoutingTable", "RTABLE")
    self.router.getRoutingTable().load(rtFile)

    self.router.pox = pox.PacketInjectorPrx.checkedCast(self.communicator().propertyToProxy("SimpleRouter.Proxy").ice_twoway())
    if not self.router.pox:
      log.error("ERROR: Cannot connect to POX controller or invalid configuration of the controller")
      return -1

    ifFile = self.communicator().getProperties().getPropertyWithDefault("Ifconfig", "IP_CONFIG")
    self.router.loadIfconfig(ifFile)

    adapter = self.communicator().createObjectAdapter("")
    ident = Ice.Identity()
    ident.name = Ice.generateUUID()
    ident.category = ""

    adapter.add(PacketHandler(self.router), ident)
    adapter.activate()
    self.router.pox.ice_getConnection().setAdapter(adapter)
    self.router.pox.addPacketHandler(ident)

    ifaces = self.router.pox.getIfaces()
    self.router.reset(ifaces)

    def poxPinger(self):
        while not self.shouldStop:
            time.sleep(1)
            try:
                self.router.pox.ice_ping()
            except:
                print("Connection to POX service broken, exiting...", file=sys.stderr)
                self.communicator().shutdown()
    
    self.shouldStop = False
    checkThread = threading.Thread(target=poxPinger, args=(self,))
    checkThread.start()

    testAdapter = self.communicator().createObjectAdapterWithEndpoints("Tester", "tcp -p 65500")
    testAdapter.add(Tester(self.router), self.communicator().stringToIdentity("Tester"))
    testAdapter.activate()

    self.communicator().waitForShutdown()
    self.shouldStop = True
    self.router.arpCache.stop()
    checkThread.join()
    return 0
