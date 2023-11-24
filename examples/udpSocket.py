#!/usr/bin/env python
# -*- coding: utf8 -*-

#   Copyright 2023 Przemyslaw Bereski https://github.com/przemobe/

#   MicroPython RP2
#   ENC28J60 (https://github.com/przemobe/micropy-ENC28J60) and
#   microCoAPy (https://github.com/insighio/microCoAPy) integration.

#   Custom socket implementation.

class UdpSocket:
    def __init__(self, ntw, localPort):
        self.ntw = ntw
        self.localPort = localPort
        self.rxQueue = []
        self.debug = False
        self.warning = True
        self.ntw.registerUdp4Callback(self.localPort, self.handleIncomingPacket)


    def __del__(self):
        self.close()


    def close(self):
        self.ntw.registerUdp4Callback(self.localPort, None)


    def sendto(self, txBytes, address):
        if self.debug:
            print(f'[UdpSocket] Sending {len(txBytes)} bytes to: {str(address)}')
        addressIp = bytes([int(x) for x in address[0].split('.')])

        if not self.ntw.isConnectedIp4(addressIp):
            self.ntw.connectIp4(addressIp)
            if self.warning:
                print(f'[UdpSocket] Not reachable address: {address[0]}!')
            return -1

        n = self.ntw.sendUdp4(addressIp, address[1], txBytes, 5683)
        return n


    def recvfrom(self, bufSize):
        if 0 == len(self.rxQueue):
            return (None, ('', 0)) # (buffer, remoteAddress), None in case no data

        rxData = self.rxQueue.pop(0)
        if self.debug:
            print(f'[UdpSocket] Receiving {len(rxData[0])} bytes to bufffer size {bufSize}')

        if bufSize < len(rxData[0]):
            rxData[0] = rxData[0][0:bufSize]

        return rxData # (buffer, remoteAddress)


    def recv(bufSize):
        return self.recvfrom(bufSize)[0]


    def setblocking(self, flag):
        # blocking is not supported.
        pass


    def handleIncomingPacket(self, pkt):
        remoteAddress = (f'{pkt.ip_src_addr[0]}.{pkt.ip_src_addr[1]}.{pkt.ip_src_addr[2]}.{pkt.ip_src_addr[3]}', pkt.udp_srcPort)

        if self.debug:
            print(f'[UdpSocket] Equeue received {len(pkt.udp_data)} bytes from: {str(remoteAddress)}')

        self.ntw.addArpEntry(pkt.ip_src_addr, pkt.eth_src)
        self.rxQueue.append((bytes(pkt.udp_data), remoteAddress))
