#!/usr/bin/env python
# -*- coding: utf8 -*-

#  Copyright 2022-2024 Przemyslaw Bereski https://github.com/przemobe/
#  This is version for MicroPython v1.17

#  Python DNS Client
#  A simple DNS client similar to 'nslookup' or 'host'.
#  Does not use any DNS libraries.
#  Reference: RFC1035, RFC3596

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
import sys
import struct
import time


DNS_DEFAULT_PORT = const(53)

DNS_RECORD_TYPE_A = const(1)  # a host address
DNS_RECORD_TYPE_NS = const(2)  # an authoritative name server
DNS_RECORD_TYPE_MD = const(3)  # a mail destination (Obsolete - use MX)
DNS_RECORD_TYPE_MF = const(4)  # a mail forwarder (Obsolete - use MX)
DNS_RECORD_TYPE_CNAME = const(5)  # the canonical name for an alias
DNS_RECORD_TYPE_SOA = const(6)  # marks the start of a zone of authority
DNS_RECORD_TYPE_MB = const(7)  # a mailbox domain name (EXPERIMENTAL)
DNS_RECORD_TYPE_MG = const(8)  # a mail group member (EXPERIMENTAL)
DNS_RECORD_TYPE_MR = const(9)  # a mail rename domain name (EXPERIMENTAL)
DNS_RECORD_TYPE_NULL = const(10)  # a null RR (EXPERIMENTAL)
DNS_RECORD_TYPE_WKS = const(11)  # a well known service description
DNS_RECORD_TYPE_PTR = const(12)  # a domain name pointer
DNS_RECORD_TYPE_HINFO = const(13)  # host information
DNS_RECORD_TYPE_MINFO = const(14)  # mailbox or mail list information
DNS_RECORD_TYPE_MX = const(15)  # mail exchange
DNS_RECORD_TYPE_TXT = const(16)  # text strings
DNS_RECORD_TYPE_AAAA = const(28)  # IP6 Address

DNS_CLASS_IN = const(1)  # the Internet
DNS_CLASS_CS = const(2)  # the CSNET class
DNS_CLASS_CH = const(3)  # the CHAOS class
DNS_CLASS_HS = const(4)  # Hesiod [Dyer 87]

DNS_RCODE_NOERROR = const(0)
DNS_RCODE_FORMATERROR = const(1)
DNS_RCODE_SERVERFAILURE = const(2)
DNS_RCODE_NONEXISTENTDOMAIN = const(3)
DNS_RCODE_NOTIMPLEMENTED = const(4)
DNS_RCODE_REFUSED = const(5)
DNS_RCODE_INT_TIMOUT = const(0x10) # internal code

DNS_MSG_SIZEMAX = const(512)

DNS_MSG_HDR_FMT = '!HHHHHH'
DNS_MSG_HDR_SIZE = const(12)

DNS_MSG_HDR_FLAGS_QR = const(0x8000) # query (0), response (1)
DNS_MSG_HDR_FLAGS_OP = const(0x7800) # op. code
DNS_MSG_HDR_FLAGS_OP_QUERY = const(0 << 11)
DNS_MSG_HDR_FLAGS_OP_IQUERY = const(1 << 11)
DNS_MSG_HDR_FLAGS_OP_STATUS = const(2 << 11)
DNS_MSG_HDR_FLAGS_AA = const(0x0400) # Authoritative Answer
DNS_MSG_HDR_FLAGS_TC = const(0x0200) # TrunCation
DNS_MSG_HDR_FLAGS_RD = const(0x0100) # Recursion Desired
DNS_MSG_HDR_FLAGS_RA = const(0x0080) # Recursion Available
DNS_MSG_HDR_FLAGS_RC = const(0x000F) # Response code


class DnsClientCore():
    def proc_name(self, msg, idx):
        # Helper function processing names in response
        while True:
            label_len = msg[idx]
            idx += 1
            if 0xC0 == (label_len & 0xC0):
                pointer = ((label_len & 0x3F) << 8) | msg[idx]
                idx += 1
                break  # after a pointer there is no more labels
            elif 0 != label_len:
                idx += label_len
            else:
                break  # 0 indicates last label
        return idx


    def proc_response(self, rx_buff, q_type):
        # Helper function processing response
        msg = memoryview(rx_buff)

        # Process Header
        hdr_id, hdr_flags, hdr_qdcount, hdr_ancount, hdr_nscount, hdr_arcount = struct.unpack_from(
            DNS_MSG_HDR_FMT, msg)
        idx = DNS_MSG_HDR_SIZE
        #print('DBG header: id=0x{:04x} flags=0x{:04x} qd_cnt={} an_cnt={} ns_cnt={} ar_cnt={}'.format(hdr_id, hdr_flags, hdr_qdcount, hdr_ancount, hdr_nscount, hdr_arcount))
        response_code = hdr_flags & DNS_MSG_HDR_FLAGS_RC
        result = (response_code, None, 0)

        if DNS_RCODE_NOERROR != response_code:
            return result

        # Process Question section only
        for q_idx in range(hdr_qdcount):
            idx = self.proc_name(msg, idx)
            #q_type, q_class = struct.unpack_from('!HH', msg, idx)
            idx += 4

        # Process Record section Answer only first record
        for elem_idx in range(hdr_ancount):
            idx = self.proc_name(msg, idx)
            rr_type, rr_class, rr_ttl, rr_rd_length = struct.unpack_from(
                '!HHIH', msg, idx)
            idx += 10
            rr_data = msg[idx: idx + rr_rd_length]
            idx += rr_rd_length

            if q_type == rr_type:
                return response_code, bytes(rr_data), rr_ttl

        return result


    def get_query_id_from(self, rx_buff):
        # Helper function to read query id from rx_buff
        q_id, = struct.unpack_from('!H', rx_buff)
        return q_id


    def fill_query(self, tx_buff, host_name, identifier, q_type=DNS_RECORD_TYPE_A):
        # Helper function to fill tx_buff with query. Returs query length.
        tx_msg = memoryview(tx_buff)

        idx = 0

        # Header
        hdr_flags = DNS_MSG_HDR_FLAGS_OP_QUERY | DNS_MSG_HDR_FLAGS_RD
        hdr_qdcount = 1
        hdr_ancount = 0
        hdr_nscount = 0
        hdr_arcount = 0
        struct.pack_into(
            DNS_MSG_HDR_FMT,
            tx_msg,
            idx,
            identifier,
            hdr_flags,
            hdr_qdcount,
            hdr_ancount,
            hdr_nscount,
            hdr_arcount)
        idx += DNS_MSG_HDR_SIZE

        # Construct the QNAME:
        # size|label|size|label|size|...|label|0x00
        for label in host_name.split("."):
            label_bytes = label.strip().encode()
            label_len = len(label_bytes)
            tx_msg[idx] = label_len
            idx += 1
            tx_msg[idx: idx + label_len] = label_bytes
            idx += label_len
        tx_msg[idx] = 0
        idx += 1

        # QTYPE + QCLASS
        struct.pack_into('!HH', tx_msg, idx, q_type, DNS_CLASS_IN)
        idx += 4

        return idx


class DnsClientBase(DnsClientCore):
    def __init__(self):
        self.server_ip = None
        self.server_port = DNS_DEFAULT_PORT

        # Queries data
        self.q_id = 0 # next query id
        self.query_dic = {} # q_id : (sent_count, hostname, q_type, q_sent_time, callback(hostname, status, addr | None, ttl))


    def set_serv_addr(self, server_ip, server_port=DNS_DEFAULT_PORT):
        # Public DNS server address setter
        self.server_ip = server_ip
        self.server_port = server_port


    def proc_rx_msg(self, rx_msg):
        # Function process received message
        ctime = time.time()
        q_id = self.get_query_id_from(rx_msg)
        if q_id not in self.query_dic:
            print(f'[DNS-C] Rx resposne ID={q_id}: query not found!')
            return

        sent_count, hostname, q_type, q_sent_time, callback = self.query_dic.pop(q_id)
        resp = self.proc_response(rx_msg, q_type)

        if (DNS_RCODE_NOERROR != resp[0]) or (resp[1] is None):
            print(f'[DNS-C] ID={q_id} "{hostname}" address fail to resolve')
        else:
            a = resp[1]
            print(f'[DNS-C] ID={q_id} "{hostname}" at {a[0]}.{a[1]}.{a[2]}.{a[3]} TTL={resp[2]}')

        if callback is not None:
            callback(hostname, resp[0], resp[1], resp[2])


    def proc_queries(self):
        # Function process pending queries
        if self.server_ip is None:
            return

        ctime = time.time()
        tx_buff = bytearray(DNS_MSG_SIZEMAX)
        timeout_list = []

        for q_id, q_info in self.query_dic.items():
            if (0 != q_info[0]) and (ctime - q_info[3] < 3):
                continue

            if 5 < q_info[0]:
                timeout_list.append(q_id)
                continue

            tx_len = self.fill_query(tx_buff, q_info[1], q_id, q_info[2])
            tx_msg = memoryview(tx_buff)
            n = self.send_query(tx_msg[0:tx_len])
            if 0 < n:
                 self.query_dic[q_id] = (q_info[0] + 1, q_info[1], q_info[2], ctime, q_info[4])

        for q_id in timeout_list:
            sent_count, hostname, q_type, q_sent_time, callback = self.query_dic.pop(q_id)
            if callback is not None:
                callback(hostname, DNS_RCODE_INT_TIMOUT, None, 0)


    def resolve_host_name(self, hostname, callback=None, q_type=DNS_RECORD_TYPE_A):
        # Public function to create DNS query
        # hostname - host name to resolve
        # callback - function callback(status, addr | None, ttl)
        # q_type   - query type: A, AAAA, ...

        # Check if query is not already pending
        for q_info in self.query_dic.values():
            if hostname == q_info[1]:
                return

        self.query(hostname, callback, q_type)
        return


    def query(self, hostname, callback, q_type):
        # Public function to create DNS query
        self.query_dic[self.q_id] = (0, hostname, q_type, 0, callback)
        self.q_id += 1
        if self.q_id > 0xFFFF:
            self.q_id = 0


    def loop(self):
        # Public function to be called in main loop
        if len(self.query_dic):
            self.receive()
        self.proc_queries()


    def send_query(self, tx_msg):
        # Function shall implement sending UDP
        raise NotImplementedError


    def receive(self):
        # Function shall implement receiving and processing UDP
        raise NotImplementedError


class DnsClientSock(DnsClientBase):
    # This class is intended to be used with standard or user defined socket
    def __init__(self, socket):
        DnsClientBase.__init__(self)

        # The socket must support functions:
        # * socket.sendto(bytes, address)
        # * socket.recvfrom(bufsize)
        # * socket.setblocking(flag=False)
        self.socket = socket


    def send_query(self, tx_msg):
        return self.socket.sendto(tx_msg, (self.server_ip, self.server_port))


    def receive(self):
        self.socket.setblocking(False)
        while True:
            try:
                rx_msg, remote_addr = self.socket.recvfrom(DNS_MSG_SIZEMAX)
                if rx_msg is None:
                    break
            except:
                break

            if remote_addr != (self.server_ip, self.server_port):
                print(f'[DNS-C] Unexpected server address {remote_addr}!')
                break

            self.proc_rx_msg(rx_msg)


class DnsClientNtw(DnsClientBase):
    # This class is intended to be used with network class:
    # https://github.com/przemobe/micropy-ENC28J60/blob/main/examples/Ntw.py
    def __init__(self, ntw, my_port):
        DnsClientBase.__init__(self)

        self.ntw = ntw
        self.my_port = my_port

        # register msg callback
        self.ntw.registerUdp4Callback(self.my_port, self.receive_callback)


    def receive_callback(self, pkt):
        # Callback function for processing received packed
        if pkt.ip_src_addr != self.server_ip or pkt.udp_srcPort != self.server_port:
            print(f'[DNS-C] Unexpected server address {pkt.ip_src_addr}:{pkt.udp_srcPort}!')
            return

        self.proc_rx_msg(pkt.udp_data)


    def send_query(self, tx_msg):
        if not self.ntw.isConnectedIp4(self.server_ip):
            self.ntw.connectIp4(self.server_ip)
            return 0

        return self.ntw.sendUdp4(self.server_ip, self.server_port, tx_msg, self.my_port)


    def receive(self):
        pass
