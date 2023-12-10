#!/usr/bin/env python
# -*- coding: utf8 -*-

#  Copyright 2022 Przemyslaw Bereski https://github.com/przemobe/

#  This is version for MicroPython v1.17

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


from micropython import const
from machine import Pin
from machine import SPI
import struct
import random
import time
from collections import OrderedDict
import Ntw


DHCP4_PORT_SERVER   = const(67)
DHCP4_PORT_CLIENT   = const(68)

DHCP4_OP_REQUEST    = const(1)
DHCP4_OP_REPLY      = const(2)

DHCP4_FLAG_BROADCAST = const(0x8000)

DHCP4_MAGIC_INT     = const(0x63825363)
DHCP4_MAGIC_BYTES   = bytes([0x63, 0x82, 0x53, 0x63])
DHCP4_MAGIC_SIZE    = const(4)

# DHCP message type values
DHCP4_MSG_TYPE_DISCOVER     = const(1)
DHCP4_MSG_TYPE_OFFER        = const(2)
DHCP4_MSG_TYPE_REQUEST      = const(3)
DHCP4_MSG_TYPE_DECLINE      = const(4)
DHCP4_MSG_TYPE_ACK          = const(5)
DHCP4_MSG_TYPE_NAK          = const(6)
DHCP4_MSG_TYPE_RELEASE      = const(7)
DHCP4_MSG_TYPE_INFORM       = const(8)

# DHCP option codes
DHCP4_OPT_PAD               = const(0)
DHCP4_OPT_SUBNETMASK        = const(1)
DHCP4_OPT_TIMEOFFSET        = const(2)
DHCP4_OPT_ROUTER            = const(3)
DHCP4_OPT_TIMESERVER        = const(4)
DHCP4_OPT_NAMESERVER        = const(5)
DHCP4_OPT_DNS_SVRS          = const(6)
DHCP4_OPT_LOGSERV           = const(7)
DHCP4_OPT_COOKIESERV        = const(8)
DHCP4_OPT_LPRSERV           = const(9)
DHCP4_OPT_IMPSERV           = const(10)
DHCP4_OPT_RESSERV           = const(11)
DHCP4_OPT_HOSTNAME          = const(12)
DHCP4_OPT_BOOTFILESIZE      = const(13)
DHCP4_OPT_DUMPFILE          = const(14)
DHCP4_OPT_DOMAIN            = const(15)
DHCP4_OPT_SWAPSERV          = const(16)
DHCP4_OPT_ROOTPATH          = const(17)
DHCP4_OPT_EXTENPATH         = const(18)
DHCP4_OPT_IPFORWARD         = const(19)
DHCP4_OPT_SRCROUTE          = const(20)
DHCP4_OPT_POLICYFILTER      = const(21)
DHCP4_OPT_MAXASMSIZE        = const(22)
DHCP4_OPT_IPTTL             = const(23)
DHCP4_OPT_MTUTIMEOUT        = const(24)
DHCP4_OPT_MTUTABLE          = const(25)
DHCP4_OPT_MTUSIZE           = const(26)
DHCP4_OPT_LOCALSUBNETS      = const(27)
DHCP4_OPT_BROADCASTADDR     = const(28)
DHCP4_OPT_DOMASKDISCOV      = const(29)
DHCP4_OPT_MASKSUPPLY        = const(30)
DHCP4_OPT_DOROUTEDISC       = const(31)
DHCP4_OPT_ROUTERSOLICIT     = const(32)
DHCP4_OPT_STATICROUTE       = const(33)
DHCP4_OPT_TRAILERENCAP      = const(34)
DHCP4_OPT_ARPTIMEOUT        = const(35)
DHCP4_OPT_ETHERENCAP        = const(36)
DHCP4_OPT_TCPTTL            = const(37)
DHCP4_OPT_TCPKEEPALIVE      = const(38)
DHCP4_OPT_TCPALIVEGARBAGE   = const(39)
DHCP4_OPT_NISDOMAIN         = const(40)
DHCP4_OPT_NISSERVERS        = const(41)
DHCP4_OPT_NISTIMESERV       = const(42)
DHCP4_OPT_VENDSPECIFIC      = const(43)
DHCP4_OPT_NBNS              = const(44)
DHCP4_OPT_NBDD              = const(45)
DHCP4_OPT_NBTCPIP           = const(46)
DHCP4_OPT_NBTCPSCOPE        = const(47)
DHCP4_OPT_XFONT             = const(48)
DHCP4_OPT_XDISPLAYMGR       = const(49)
DHCP4_OPT_REQ_IP            = const(50)
DHCP4_OPT_LEASE_SEC         = const(51)
DHCP4_OPT_OPTIONOVERLOAD    = const(52)
DHCP4_OPT_MSGTYPE           = const(53)
DHCP4_OPT_SERVER_ID         = const(54)
DHCP4_OPT_PARAM_REQ         = const(55)
DHCP4_OPT_MESSAGE           = const(56)
DHCP4_OPT_MAXMSGSIZE        = const(57)
DHCP4_OPT_RENEWTIME         = const(58)
DHCP4_OPT_REBINDTIME        = const(59)
DHCP4_OPT_VENDOR_ID         = const(60)
DHCP4_OPT_CLIENT_ID         = const(61)
DHCP4_OPT_NISPLUSDOMAIN     = const(64)
DHCP4_OPT_NISPLUSSERVERS    = const(65)
DHCP4_OPT_MOBILEIPAGENT     = const(68)
DHCP4_OPT_SMTPSERVER        = const(69)
DHCP4_OPT_POP3SERVER        = const(70)
DHCP4_OPT_NNTPSERVER        = const(71)
DHCP4_OPT_WWWSERVER         = const(72)
DHCP4_OPT_FINGERSERVER      = const(73)
DHCP4_OPT_IRCSERVER         = const(74)
DHCP4_OPT_STSERVER          = const(75)
DHCP4_OPT_STDASERVER        = const(76)
DHCP4_OPT_END               = const(255)

# DHCP message fields
DHCP4_MSG_FIELD_OP      = const(0)
DHCP4_MSG_FIELD_HTYPE   = const(1)
DHCP4_MSG_FIELD_HLEN    = const(2)
DHCP4_MSG_FIELD_HOPS    = const(3)
DHCP4_MSG_FIELD_XID     = const(4)
DHCP4_MSG_FIELD_SECS    = const(5)
DHCP4_MSG_FIELD_FLAGS   = const(6)
DHCP4_MSG_FIELD_CIADDR  = const(7)
DHCP4_MSG_FIELD_YIADDR  = const(8)
DHCP4_MSG_FIELD_SIADDR  = const(9)
DHCP4_MSG_FIELD_GIADDR  = const(10)
DHCP4_MSG_FIELD_CHADDR  = const(11)
DHCP4_MSG_FIELD_SNAME   = const(12)
DHCP4_MSG_FIELD_FILE    = const(13)
DHCP4_MSG_HDR_FMT       = '!BBBBIHH4s4s4s4s16s64s128s'
DHCP4_MSG_HDR_SIZE      = const(236)

class Dhcp4Client():
    class ClientState_Base():
        def get_state_name(self):
            return 'Base'

        def loop(self, ctx):
            print(f'[DHCP-C] loop in {self.get_state_name():s} state')

        def proc_rx_pkt(self, ctx, pkt):
            print(f'[DHCP-C] process pkt in {self.get_state_name():s} state')

    class ClientState_Init(ClientState_Base):
        def get_state_name(self):
            return 'Init'

        def loop(self, ctx):
            if False == ctx.ntw.nic.IsLinkUp():
                return

            ctx.init_time = time.time()
            ctx.xid =  random.getrandbits(32)
            ctx.renew_attemp_cnt = 0
            print(f"[DHCP-C] Tx Discovery in state={self.get_state_name():s} xid=0x{ctx.xid:x}")

            data = ctx.make_discover_msg()
            n = ctx.ntw.sendUdp4Bcast(DHCP4_PORT_SERVER, DHCP4_PORT_CLIENT, data)
            if 0 > n:
                print(f'sendUdp4Bcast error={n} - go to Init state')
                # keep Init state
                return

            ctx.ntw.registerUdp4BcastCallback(DHCP4_PORT_CLIENT, ctx.proc_rx_pkt)
            # change the state
            ctx.state = Dhcp4Client.ClientState_AwaitOffer()

    class ClientState_AwaitOffer(ClientState_Base):
        def get_state_name(self):
            return 'AwaitOffer'

        def loop(self, ctx):
            ctime = time.time()
            if ctime - ctx.init_time > 5:
                # change the state
                ctx.state = Dhcp4Client.ClientState_Init()

        def proc_rx_pkt(self, ctx, pkt):
            print(f'[DHCP-C] process pkt in {self.get_state_name():s} state')
            rxMsg = Dhcp4Packet()
            rxMsg.unpack(pkt.udp_data)

            if (DHCP4_OP_REPLY != rxMsg.fields[DHCP4_MSG_FIELD_OP]):
                print('[DHCP-C] op mismatch')
                return
            if (ctx.xid != rxMsg.fields[DHCP4_MSG_FIELD_XID]):
                print(f'[DHCP-C] xid mismatch: 0x{ctx.xid:x} vs 0x{rxMsg.fields[DHCP4_MSG_FIELD_XID]}')
                return
            if (1 != rxMsg.fields[DHCP4_MSG_FIELD_HTYPE]) or (6 != rxMsg.fields[DHCP4_MSG_FIELD_HLEN]) or (ctx.ntw.myMacAddr != rxMsg.fields[DHCP4_MSG_FIELD_CHADDR][0:6]):
                print('[DHCP-C] Client mac address mismatch')
                return
            if DHCP4_MSG_TYPE_OFFER != rxMsg.options[DHCP4_OPT_MSGTYPE][0]:
                print(f'[DHCP-C] Unexpected msg type={rxMsg.options[DHCP4_OPT_MSGTYPE][0]} in state={self.get_state_name():s}')
                # change the state
                ctx.state = Dhcp4Client.ClientState_Init()
                return

            print(f'[DHCP-C] Rx Offer in state={self.get_state_name():s} xid=0x{ctx.xid:x}')
            ctx.yiaddr = rxMsg.fields[DHCP4_MSG_FIELD_YIADDR]
            ctx.siaddr = rxMsg.fields[DHCP4_MSG_FIELD_SIADDR]

            print(f"[DHCP-C] Tx Request in state={self.get_state_name():s} xid=0x{ctx.xid:x}")
            data = ctx.make_request_offer()
            n = ctx.ntw.sendUdp4Bcast(DHCP4_PORT_SERVER, DHCP4_PORT_CLIENT, data)
            if 0 > n:
                print(f'sendUdp4Bcast error={n} - go to Init state')
                # change the state
                ctx.state = Dhcp4Client.ClientState_Init()
                return
            # change the state
            ctx.state = Dhcp4Client.ClientState_Selecting()

    class ClientState_Selecting(ClientState_Base):
        '''Await ACK'''
        def get_state_name(self):
            return 'Selecting'

        def loop(self, ctx):
            ctime = time.time()
            if ctime - ctx.init_time > 10:
                # change the state
                ctx.state = Dhcp4Client.ClientState_Init()

        def proc_rx_pkt(self, ctx, pkt):
            print(f'[DHCP-C] process pkt in {self.get_state_name():s} state')
            rxMsg = Dhcp4Packet()
            rxMsg.unpack(pkt.udp_data)

            if (DHCP4_OP_REPLY != rxMsg.fields[DHCP4_MSG_FIELD_OP]):
                print('[DHCP-C] op mismatch')
                return
            if (ctx.xid != rxMsg.fields[DHCP4_MSG_FIELD_XID]):
                print(f'[DHCP-C] xid mismatch: 0x{ctx.xid:x} vs 0x{rxMsg.fields[DHCP4_MSG_FIELD_XID]}')
                return
            if (1 != rxMsg.fields[DHCP4_MSG_FIELD_HTYPE]) or (6 != rxMsg.fields[DHCP4_MSG_FIELD_HLEN]) or (ctx.ntw.myMacAddr != rxMsg.fields[DHCP4_MSG_FIELD_CHADDR][0:6]):
                print('[DHCP-C] Client mac address mismatch')
                return
            if DHCP4_MSG_TYPE_ACK != rxMsg.options[DHCP4_OPT_MSGTYPE][0]:
                print(f'[DHCP-C] Unexpected msg type={rxMsg.options[DHCP4_OPT_MSGTYPE][0]} in state={self.get_state_name():s}')
                # change the state
                ctx.state = Dhcp4Client.ClientState_Init()
                return

            print(f'[DHCP-C] Rx Ack in state={self.get_state_name():s} xid=0x{ctx.xid:x}')
            ctx.yiaddr = rxMsg.fields[DHCP4_MSG_FIELD_YIADDR]
            ctx.siaddr = rxMsg.fields[DHCP4_MSG_FIELD_SIADDR]

            # set new IP addr
            a = ctx.yiaddr
            print(f'[DHCP-C] new IP address {a[0]}.{a[1]}.{a[2]}.{a[3]}')
            a = rxMsg.options[DHCP4_OPT_SUBNETMASK]
            print(f'[DHCP-C] SUBNETMASK {a[0]}.{a[1]}.{a[2]}.{a[3]}')
            a = rxMsg.options[DHCP4_OPT_ROUTER]
            print(f'[DHCP-C] ROUTER {a[0]}.{a[1]}.{a[2]}.{a[3]}')

            ctx.ntw.setIPv4(ctx.yiaddr, rxMsg.options[DHCP4_OPT_SUBNETMASK], rxMsg.options[DHCP4_OPT_ROUTER])
            ctx.ntw.addArpEntry(ctx.siaddr, pkt.eth_src)

            # set DNS server address
            a = rxMsg.options.get(DHCP4_OPT_DNS_SVRS)
            if a is not None:
                print(f'[DHCP-C] DNS_SVRS {a[0]}.{a[1]}.{a[2]}.{a[3]}')
                ctx.ntw.setDnsSrvIpv4(a)

            # set timers
            '''
            Times T1 and T2 are configurable by the server through options.  T1
            defaults to (0.5 * duration_of_lease).  T2 defaults to (0.875 *
            duration_of_lease).
            '''
            ctx.bound_time = time.time()
            ctx.lease_seconds = 86400
            if DHCP4_OPT_LEASE_SEC in rxMsg.options:
                ctx.lease_seconds = struct.unpack("!I", rxMsg.options[DHCP4_OPT_LEASE_SEC])[0]
                print(f'[DHCP-C] Rx Lease time {ctx.lease_seconds} s')
            ctx.renewal_seconds = round(0.5 * ctx.lease_seconds)
            ctx.rebinding_seconds = round(0.875 * ctx.lease_seconds)
            if DHCP4_OPT_RENEWTIME in rxMsg.options:
                ctx.renewal_seconds = struct.unpack("!I", rxMsg.options[DHCP4_OPT_RENEWTIME])[0]
                print(f'[DHCP-C] Rx Renewal time (T1) {ctx.renewal_seconds} s')
            if DHCP4_OPT_REBINDTIME in rxMsg.options:
                ctx.rebinding_seconds = struct.unpack("!I", rxMsg.options[DHCP4_OPT_REBINDTIME])[0]
                print(f'[DHCP-C] Rx Rebinding time (T2) {ctx.rebinding_seconds} s')

            # deregister UDP BCast
            ctx.ntw.registerUdp4BcastCallback(DHCP4_PORT_CLIENT, None)

            # change the state
            ctx.state = Dhcp4Client.ClientState_Bound()

    class ClientState_Bound(ClientState_Base):
        def get_state_name(self):
            return 'Bound'

        def loop(self, ctx):
            ctime = time.time()
            if ctime - ctx.bound_time > ctx.renewal_seconds:
                print(f"[DHCP-C] Renewal timer expires after {ctx.renewal_seconds} s")
                # change the state
                ctx.renew_attemp_cnt = 0
                ctx.state = Dhcp4Client.ClientState_RenewingInit()

    class ClientState_RenewingInit(ClientState_Base):
        def get_state_name(self):
            return 'RenewingInit'

        def loop(self, ctx):
            ctx.init_time = time.time()
            ctx.xid =  random.getrandbits(32)

            print(f"[DHCP-C] Tx Request in state={self.get_state_name():s} xid=0x{ctx.xid:x}")
            data = ctx.make_request_renew()
            n = ctx.ntw.sendUdp4(ctx.siaddr, DHCP4_PORT_SERVER, data, DHCP4_PORT_CLIENT)
            if 0 > n:
                print(f'sendUdp4 error={n} - go to Init state')
                # change the state
                ctx.state = Dhcp4Client.ClientState_Init()
                return

            ctx.ntw.registerUdp4Callback(DHCP4_PORT_CLIENT, ctx.proc_rx_pkt)
            # change the state
            ctx.renew_attemp_cnt += 1
            ctx.state = Dhcp4Client.ClientState_Renewing()

        def proc_rx_pkt(self, ctx, pkt):
            pass

    class ClientState_Renewing(ClientState_Base):
        def get_state_name(self):
            return 'Renewing'

        def loop(self, ctx):
            ctime = time.time()
            if (ctime - ctx.bound_time > ctx.rebinding_seconds) or (ctime -  ctx.bound_time > ctx.lease_seconds) or (3 < ctx.renew_attemp_cnt):
                # change the state
                ctx.state = Dhcp4Client.ClientState_Init()
            elif ctime - ctx.init_time > 5:
                # change the state
                ctx.state = Dhcp4Client.ClientState_RenewingInit()

        def proc_rx_pkt(self, ctx, pkt):
            print(f'[DHCP-C] process pkt in {self.get_state_name():s} state')
            rxMsg = Dhcp4Packet()
            rxMsg.unpack(pkt.udp_data)

            if (DHCP4_OP_REPLY != rxMsg.fields[DHCP4_MSG_FIELD_OP]):
                print('[DHCP-C] op mismatch')
                return
            if (ctx.xid != rxMsg.fields[DHCP4_MSG_FIELD_XID]):
                print(f'[DHCP-C] xid mismatch: 0x{ctx.xid:x} vs 0x{rxMsg.fields[DHCP4_MSG_FIELD_XID]}')
                return
            if (1 != rxMsg.fields[DHCP4_MSG_FIELD_HTYPE]) or (6 != rxMsg.fields[DHCP4_MSG_FIELD_HLEN]) or (ctx.ntw.myMacAddr != rxMsg.fields[DHCP4_MSG_FIELD_CHADDR][0:6]):
                print('[DHCP-C] Client mac address mismatch')
                return
            if DHCP4_MSG_TYPE_ACK != rxMsg.options[DHCP4_OPT_MSGTYPE][0]:
                print(f'[DHCP-C] Unexpected msg type={rxMsg.options[DHCP4_OPT_MSGTYPE][0]} in state={self.get_state_name():s}')
                # change the state
                ctx.state = Dhcp4Client.ClientState_Init()
                return

            print(f'[DHCP-C] Rx Ack in state={self.get_state_name():s} xid=0x{ctx.xid:x}')
            ctx.yiaddr = rxMsg.fields[DHCP4_MSG_FIELD_YIADDR]
            ctx.siaddr = rxMsg.fields[DHCP4_MSG_FIELD_SIADDR]

            # set new IP addr
            a = ctx.yiaddr
            print(f'[DHCP-C] new IP address {a[0]}.{a[1]}.{a[2]}.{a[3]}')
            a = rxMsg.options[DHCP4_OPT_SUBNETMASK]
            print(f'[DHCP-C] SUBNETMASK {a[0]}.{a[1]}.{a[2]}.{a[3]}')
            a = rxMsg.options[DHCP4_OPT_ROUTER]
            print(f'[DHCP-C] ROUTER {a[0]}.{a[1]}.{a[2]}.{a[3]}')

            ctx.ntw.setIPv4(ctx.yiaddr, rxMsg.options[DHCP4_OPT_SUBNETMASK], rxMsg.options[DHCP4_OPT_ROUTER])
            ctx.ntw.addArpEntry(ctx.siaddr, pkt.eth_src)

            # set DNS server address
            a = rxMsg.options.get(DHCP4_OPT_DNS_SVRS)
            if a is not None:
                print(f'[DHCP-C] DNS_SVRS {a[0]}.{a[1]}.{a[2]}.{a[3]}')
                ctx.ntw.setDnsSrvIpv4(a)

            # set timers
            '''
            Times T1 and T2 are configurable by the server through options.  T1
            defaults to (0.5 * duration_of_lease).  T2 defaults to (0.875 *
            duration_of_lease).
            '''
            ctx.bound_time = time.time()
            ctx.lease_seconds = 86400
            if DHCP4_OPT_LEASE_SEC in rxMsg.options:
                ctx.lease_seconds = struct.unpack("!I", rxMsg.options[DHCP4_OPT_LEASE_SEC])[0]
                print(f'[DHCP-C] Rx Lease time {ctx.lease_seconds} s')
            ctx.renewal_seconds = round(0.5 * ctx.lease_seconds)
            ctx.rebinding_seconds = round(0.875 * ctx.lease_seconds)
            if DHCP4_OPT_RENEWTIME in rxMsg.options:
                ctx.renewal_seconds = struct.unpack("!I", rxMsg.options[DHCP4_OPT_RENEWTIME])[0]
                print(f'[DHCP-C] Rx Renewal time (T1) {ctx.renewal_seconds} s')
            if DHCP4_OPT_REBINDTIME in rxMsg.options:
                ctx.rebinding_seconds = struct.unpack("!I", rxMsg.options[DHCP4_OPT_REBINDTIME])[0]
                print(f'[DHCP-C] Rx Rebinding time (T2) {ctx.rebinding_seconds} s')

            # deregister UDP Unicastcast
            ctx.ntw.registerUdp4Callback(DHCP4_PORT_CLIENT, None)

            # change the state
            ctx.state = Dhcp4Client.ClientState_Bound()

    def __init__(self, ntw, name=None):
        self.state = Dhcp4Client.ClientState_Init()
        self.ntw = ntw
        self.name = name
        self.opt_param_req = bytes([DHCP4_OPT_SUBNETMASK, DHCP4_OPT_ROUTER, DHCP4_OPT_DNS_SVRS])

    def proc_rx_pkt(self, pkt):
        self.state.proc_rx_pkt(self, pkt)

    def loop(self):
        self.state.loop(self)

    def make_discover_msg(self):
        packet = Dhcp4Packet()
        packet.options[DHCP4_OPT_MSGTYPE] = bytes([DHCP4_MSG_TYPE_DISCOVER])
        if self.name and len(self.name):
            packet.options[DHCP4_OPT_HOSTNAME] = self.name.encode()
        packet.options[DHCP4_OPT_MAXMSGSIZE] = struct.pack('!H', self.ntw.getEthMTU())
        packet.options[DHCP4_OPT_PARAM_REQ] = self.opt_param_req
        packet.fields[DHCP4_MSG_FIELD_OP] = DHCP4_OP_REQUEST
        packet.fields[DHCP4_MSG_FIELD_XID] = self.xid
        packet.fields[DHCP4_MSG_FIELD_FLAGS] = DHCP4_FLAG_BROADCAST
        packet.fields[DHCP4_MSG_FIELD_CHADDR][0:6] = self.ntw.myMacAddr
        packet.fields[DHCP4_MSG_FIELD_HLEN] = 6
        msg = bytearray(packet.calcsize())
        packet.pack_into(msg)
        return msg

    def make_request_offer(self):
        packet = Dhcp4Packet()
        packet.options[DHCP4_OPT_MSGTYPE] = bytes([DHCP4_MSG_TYPE_REQUEST])
        packet.options[DHCP4_OPT_REQ_IP] = bytes(self.yiaddr)
        packet.options[DHCP4_OPT_SERVER_ID] = bytes(self.siaddr)
        if self.name and len(self.name):
            packet.options[DHCP4_OPT_HOSTNAME] = self.name.encode()
        packet.options[DHCP4_OPT_MAXMSGSIZE] = struct.pack('!H', self.ntw.getEthMTU())
        packet.options[DHCP4_OPT_PARAM_REQ] = self.opt_param_req
        packet.fields[DHCP4_MSG_FIELD_OP] = DHCP4_OP_REQUEST
        packet.fields[DHCP4_MSG_FIELD_XID] = self.xid
        packet.fields[DHCP4_MSG_FIELD_FLAGS] = DHCP4_FLAG_BROADCAST
        packet.fields[DHCP4_MSG_FIELD_CHADDR][0:6] = self.ntw.myMacAddr
        packet.fields[DHCP4_MSG_FIELD_HLEN] = 6
        msg = bytearray(packet.calcsize())
        packet.pack_into(msg)
        return msg

    def make_request_renew(self):
        packet = Dhcp4Packet()
        packet.options[DHCP4_OPT_MSGTYPE] = bytes([DHCP4_MSG_TYPE_REQUEST])
        packet.options[DHCP4_OPT_CLIENT_ID] = bytes([0x01]) + bytes(self.ntw.myMacAddr)
        if self.name and len(self.name):
            packet.options[DHCP4_OPT_HOSTNAME] = self.name.encode()
        packet.options[DHCP4_OPT_MAXMSGSIZE] = struct.pack('!H', self.ntw.getEthMTU())
        packet.options[DHCP4_OPT_PARAM_REQ] = self.opt_param_req
        packet.fields[DHCP4_MSG_FIELD_OP] = DHCP4_OP_REQUEST
        packet.fields[DHCP4_MSG_FIELD_XID] = self.xid
        packet.fields[DHCP4_MSG_FIELD_FLAGS] = 0
        packet.fields[DHCP4_MSG_FIELD_CIADDR][0:4] = self.yiaddr
        packet.fields[DHCP4_MSG_FIELD_CHADDR][0:6] = self.ntw.myMacAddr
        packet.fields[DHCP4_MSG_FIELD_HLEN] = 6
        msg = bytearray(packet.calcsize())
        packet.pack_into(msg)
        return msg

class Dhcp4Packet():
    '''RFC 2131'''
    def __init__(self):
        self.fields = OrderedDict()
        self.options = OrderedDict()

        self.fields[DHCP4_MSG_FIELD_OP]      = DHCP4_OP_REQUEST
        self.fields[DHCP4_MSG_FIELD_HTYPE]   = 1
        self.fields[DHCP4_MSG_FIELD_HLEN]    = 6
        self.fields[DHCP4_MSG_FIELD_HOPS]    = 0
        self.fields[DHCP4_MSG_FIELD_XID]     = 0
        self.fields[DHCP4_MSG_FIELD_SECS]    = 0
        self.fields[DHCP4_MSG_FIELD_FLAGS]   = 0
        self.fields[DHCP4_MSG_FIELD_CIADDR]  = bytearray(4)
        self.fields[DHCP4_MSG_FIELD_YIADDR]  = bytearray(4)
        self.fields[DHCP4_MSG_FIELD_SIADDR]  = bytearray(4)
        self.fields[DHCP4_MSG_FIELD_GIADDR]  = bytearray(4)
        self.fields[DHCP4_MSG_FIELD_CHADDR]  = bytearray(16)
        self.fields[DHCP4_MSG_FIELD_SNAME]   = bytearray(64)
        self.fields[DHCP4_MSG_FIELD_FILE]    = bytearray(128)

    def calcsize(self) -> int:
        size = struct.calcsize(DHCP4_MSG_HDR_FMT)
        size += 5 # 4B: Magic Coockie + 1B: End option
        for key, value in self.options.items():
            size += 2 + len(value)
        return size

    def unpack(self, frame):
        fields = struct.unpack_from(DHCP4_MSG_HDR_FMT, frame)

        self.fields[DHCP4_MSG_FIELD_OP]          = fields[0]
        self.fields[DHCP4_MSG_FIELD_HTYPE]       = fields[1]
        self.fields[DHCP4_MSG_FIELD_HLEN]        = fields[2]
        self.fields[DHCP4_MSG_FIELD_HOPS]        = fields[3]
        self.fields[DHCP4_MSG_FIELD_XID]         = fields[4]
        self.fields[DHCP4_MSG_FIELD_SECS]        = fields[5]
        self.fields[DHCP4_MSG_FIELD_FLAGS]       = fields[6]
        self.fields[DHCP4_MSG_FIELD_CIADDR][:]   = fields[7]
        self.fields[DHCP4_MSG_FIELD_YIADDR][:]   = fields[8]
        self.fields[DHCP4_MSG_FIELD_SIADDR][:]   = fields[9]
        self.fields[DHCP4_MSG_FIELD_GIADDR][:]   = fields[10]
        self.fields[DHCP4_MSG_FIELD_CHADDR][:]   = fields[11]
        self.fields[DHCP4_MSG_FIELD_SNAME][:]    = fields[12]
        self.fields[DHCP4_MSG_FIELD_FILE][:]     = fields[13]
        self.unpackOptions(frame)

    def pack_into(self, frame) -> int:
        struct.pack_into(DHCP4_MSG_HDR_FMT, frame, 0,
            self.fields[DHCP4_MSG_FIELD_OP],
            self.fields[DHCP4_MSG_FIELD_HTYPE],
            self.fields[DHCP4_MSG_FIELD_HLEN],
            self.fields[DHCP4_MSG_FIELD_HOPS],
            self.fields[DHCP4_MSG_FIELD_XID],
            self.fields[DHCP4_MSG_FIELD_SECS],
            self.fields[DHCP4_MSG_FIELD_FLAGS],
            self.fields[DHCP4_MSG_FIELD_CIADDR],
            self.fields[DHCP4_MSG_FIELD_YIADDR],
            self.fields[DHCP4_MSG_FIELD_SIADDR],
            self.fields[DHCP4_MSG_FIELD_GIADDR],
            self.fields[DHCP4_MSG_FIELD_CHADDR],
            self.fields[DHCP4_MSG_FIELD_SNAME],
            self.fields[DHCP4_MSG_FIELD_FILE])
        size = self.packoptions_into(frame)
        return size

    def unpackOptions(self, frame):
        idx = DHCP4_MSG_HDR_SIZE + DHCP4_MAGIC_SIZE
        opt = DHCP4_OPT_END
        STATE_GETOPT = 0
        STATE_GETLEN = 1
        state = STATE_GETOPT
        lenght = 0

        while idx < len(frame):
            if STATE_GETOPT == state:
                opt = frame[idx]
                idx += 1
                state = STATE_GETLEN
                if DHCP4_OPT_END == opt:
                    break
                elif DHCP4_OPT_PAD == opt:
                    continue
            else:
                lenght = frame[idx]
                idx += 1
                state = STATE_GETOPT
                self.options[opt] = bytes(frame[idx:idx+lenght])
                idx += lenght

    def packoptions_into(self, frame) -> int:
        frame[DHCP4_MSG_HDR_SIZE:DHCP4_MSG_HDR_SIZE+DHCP4_MAGIC_SIZE] = DHCP4_MAGIC_BYTES
        idx = DHCP4_MSG_HDR_SIZE + DHCP4_MAGIC_SIZE
        length = 0
        for key, value in self.options.items():
            frame[idx] = key
            idx += 1
            length = len(value)
            frame[idx] = length
            idx += 1
            frame[idx:idx+length] = value
            idx += length
        frame[idx] = DHCP4_OPT_END
        idx += 1
        return idx

if __name__ == '__main__':
    # Create network
    nicSpi = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11), miso=Pin(8))
    nicCsPin = Pin(13)
    ntw = Ntw.Ntw(nicSpi, nicCsPin)

    # Create DHCP client
    from machine import unique_id
    hostname = 'RPico-'+str(struct.unpack_from('I', unique_id()[-4:])[0])
    dhcp_client = Dhcp4Client(ntw, hostname)

    while True:
        ntw.rxAllPkt()
        dhcp_client.loop()
