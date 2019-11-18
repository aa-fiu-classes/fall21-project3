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

import struct
from enum import Enum
from functools import partial
from .ip_address import IpAddress
from .mac_address import MacAddress

ETHER_ADDR_LEN = 6
IP_MAXPACKET = 65535
ICMP_DATA_SIZE = 28

class Base:
    def __init__(self, buf=None, **kwargs):
        if buf:
            self.decode(buf)
        else:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __str__(self):
        def keyName(key):
            parts = key.split('__')
            if len(parts) == 1:
                return parts[0]
            else:
                return parts[1]
        return type(self).__name__ + ": " + " ".join(["%s=%s" % (keyName(k),v) for k,v in vars(self).items()])

# Ethernet Header
class EtherHeader(Base):
    # dhost (6 bytes): destination ethernet address
    # shost (6 bytes): source ethernet address
    # type  (2 bytes): packet type ID

    def __init__(self, buf=None, dhost = b'\0' * ETHER_ADDR_LEN, shost = b'\0' * ETHER_ADDR_LEN, type = 0):
        super().__init__(buf=buf, dhost=dhost, shost=shost, type=type)

    def encode(self):
        return struct.pack("!6s6sH", bytes(self.dhost), bytes(self.shost), self.type)

    def decode(self, packet):
        (self.dhost, self.shost, self.type) = struct.unpack("!6s6sH", packet[:14])
        return 14

    def next_level(self):
        return self.type

    def __get_mac(name, self):
        return getattr(self, "__%s" % name)

    def __set_mac(name, self, value):
        setattr(self, "__%s" % name, MacAddress(value))

    shost = property(partial(__get_mac, "shost"), partial(__set_mac, "shost"))
    dhost = property(partial(__get_mac, "dhost"), partial(__set_mac, "dhost"))

# IPv4 Header
class IpHeader(Base):
    class Protocol(Enum):
        Icmp = 1

    # v  (4 bits):   IPv4 version (4 bits)
    # hl (4 bits):   Header length (4 bits)
    # tos (1 byte):  type of service
    # len (2 bytes): total length
    # id  (2 bytes): identification
    # off (2 bytes): fragment offset field and flags
    # ttl (1 byte):  time to live
    # p   (1 byte):  protocol
    # sum (2 bytes): checksum
    # src (4 bytes): source address
    # dst (4 bytes): dest address

    def __init__(self, buf=None, hl=0, tos=0, len=0, id=0, off=0, ttl=0, p=0, sum=0, src=0, dst=0):
        super().__init__(buf=buf, v=4, hl=hl, tos=tos, len=len, id=id, off=off, ttl=ttl, p=p, sum=sum, src=src, dst=dst)

    def encode(self):
        versionAndHeaderLength = (self.v << 4) | self.hl
        return struct.pack("!BBHHHBBHLL", versionAndHeaderLength,
                           self.tos, self.len, self.id, self.off, self.ttl, self.p, self.sum, int(self.src), int(self.dst))

    def decode(self, packet):
        self.v = 0 # to preserve the order
        self.hl = 0
        (versionAndHeaderLength, self.tos, self.len, self.id, self.off, self.ttl, self.p, self.sum, self.src, self.dst) = struct.unpack("!BBHHHBBHLL", packet[:20])
        self.v = versionAndHeaderLength >> 4
        self.hl = versionAndHeaderLength & 0x0F
        return 20

    def next_level(self):
        return self.p

    def __get_ip(name, self):
        return getattr(self, "__%s" % name)

    def __set_ip(name, self, value):
        setattr(self, "__%s" % name, IpAddress(value))

    src = property(partial(__get_ip, "src"), partial(__set_ip, "src"))
    dst = property(partial(__get_ip, "dst"), partial(__set_ip, "dst"))

class ArpHeader(Base):
    class Opcode:
        Request = 1
        Reply = 2

    # hrd (2 bytes): format of hardware address
    # pro (2 bytes): format of protocol address
    # hln (1 byte):  length of hardware address
    # pln (1 byte):  length of protocol address
    # op  (2 bytes): ARP opcode (command)
    # sha (6 bytes): sender hardware address
    # sip (4 bytes): sender IPv4 address
    # tha (6 bytes): target hardware address
    # tip (4 bytes): target IP address

    def __init__(self, buf=None, pro=0, hln=0, pln=0, op=0, sha=b'\0' * ETHER_ADDR_LEN, sip=0, tha=b'\0' * ETHER_ADDR_LEN, tip=0):
        super().__init__(buf=buf, hrd=1, pro=0x0800, hln=hln, pln=pln, op=op, sha=sha, sip=sip, tha=tha, tip=tip)

    def encode(self):
        return struct.pack("!HHBBH6sL6sL", self.hrd, self.pro, self.hln, self.pln, self.op, bytes(self.sha), int(self.sip), bytes(self.tha), int(self.tip))

    def decode(self, packet):
        (self.hrd, self.pro, self.hln, self.pln, self.op, self.sha, self.sip, self.tha, self.tip) = struct.unpack("!HHBBH6sL6sL", packet[:28])
        return 28

    def __get_mac(name, self):
        return getattr(self, "__%s" % name)

    def __set_mac(name, self, value):
        if self.hrd != 1:
            raise RuntimeError("Current implementation of ArpHeader only support Ethernet addresses")
        setattr(self, "__%s" % name, MacAddress(value))

    sha = property(partial(__get_mac, "sha"), partial(__set_mac, "sha"))
    tha = property(partial(__get_mac, "tha"), partial(__set_mac, "tha"))

    def __get_ip(name, self):
        return getattr(self, "__%s" % name)

    def __set_ip(name, self, value):
        if self.pro != 0x0800:
            raise RuntimeError("Current implementation of ArpHeader only support IPv4 addresses")
        setattr(self, "__%s" % name, IpAddress(value))

    sip = property(partial(__get_ip, "sip"), partial(__set_ip, "sip"))
    tip = property(partial(__get_ip, "tip"), partial(__set_ip, "tip"))

class IcmpHeader(Base):
    # type (1 byte):  ICMP Type
    # code (2 bytes): ICMP Code
    # sum  (2 bytes): ICMP Checksum

    # if type == 3 or type == 11 or type == 4:
    #   unused (4 bytes): Unusued space
    #   data (variable length): original IP header + 8 bytes of Original Data Datagram

    # if type == 0 or type == 8:
    #   id (2 bytes):           If code = 0, an identifier to aid in matching echos and replies, may be zero.
    #   seqNum (2 bytes):       If code = 0, a sequence number to aid in matching echos and replies, may be zero.
    #   data (variable length): Opaque data

    def __init__(self, buf=None, type=0, code=0, sum=0, **kwargs):
        if buf:
            self.decode(buf)
        else:
            super().__init__(buf=buf, type=type, code=code, sum=sum)
            if self.type in [0, 8]:
                self.id = kwargs.get('id', 0)
                self.seqNum = kwargs.get('seqNum', 0)
                self.data = kwargs.get('data', b'')
            elif self.type in [3, 4, 11]:
                self.data = kwargs.get('data', b'')
            else:
                raise RuntimeError("Unsupported ICMP type: %d" % self.type)

    def encode(self):
        pkt = struct.pack("!BBH", self.type, self.code, self.sum)
        if self.type in [0, 8]:
            pkt = pkt + struct.pack("!HH", self.id, self.seqNum) + self.data
        elif self.type in [3, 4, 11]:
            pkt = pkt + struct.pack("!L", 0) + self.data
        else:
            raise RuntimeError("Unsupported ICMP type: %d" % self.type)
        return pkt

    def decode(self, packet):
        (self.type, self.code, self.sum) = struct.unpack("!BBH", packet[0:4])
        if self.type in [0, 8]:
            (self.id, self.seqNum) = struct.unpack("!HH", packet[4:8])
            self.data = packet[8:]
            return 8 + len(self.data)
        elif self.type in [3, 4, 11]:
            self.data = packet[8:]
            return 8 + len(self.data)
        else:
            raise RuntimeError("Unsupported ICMP type: %d" % self.type)

Stack = {
    EtherHeader: {
        0x0806: ArpHeader,
        0x0800: IpHeader,
        },
    IpHeader: {
        1: IcmpHeader
        }
    }
