#!/usr/bin/env python
# -*- coding: utf8 -*-

# Copyright 2022-2023 Przemyslaw Bereski https://github.com/przemobe/

from machine import Pin
from machine import SPI
from micropython import const
import Ntw
import time
import struct

# from datetime import date
# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_EPOCH_DELTA2000 = const(3155673600)
NTP_EPOCH_DELTA1970 = const(2208988800)

class SntpClient:
    '''Very simple SNTP client'''

    def __init__(self, ntw, client_port, server_addr, server_port=123, period=0):
        self.ntw = ntw
        self.client_port = client_port
        self.server_addr = bytes(server_addr)
        self.server_port = server_port
        self.period = period # seconds
        # Define states: 0 - idle, 1 - connecting, 2 - await response, 3 - done
        self.state = 0
        self.init_time = 0
        # Define output
        self.datetimetuple = None

        # Register callback for response
        self.ntw.registerUdp4Callback(self.client_port, self.proc_response)

    def loop(self):
        ctime = time.time()

        # State - idle
        if 0 == self.state:
            if not self.ntw.isIPv4Configured():
                return
            print('[SNTP] Connecting...')
            self.ntw.connectIp4(self.server_addr)
            self.init_time = ctime
            self.state = 1

        # State - connecting
        elif 1 == self.state:
            if self.ntw.isConnectedIp4(self.server_addr):
                print('[SNTP] Connected')
                self.init_time = ctime
                self.state = 2
                if 0 > self.send_request():
                    self.state = 3
                    # Deregister callback for response
                    self.ntw.registerUdp4Callback(self.client_port, None)
            elif ctime - self.init_time > 3:
                # Retry
                self.state = 0

        # State - await response
        elif 2 == self.state:
            if ctime - self.init_time > 3:
                # Retry
                self.state = 1

        # State - done, try next attempt after self.period secods
        else: # 3 == self.state
            if (0 < self.period) and (ctime - self.init_time > self.period):
                # Register callback for response
                self.ntw.registerUdp4Callback(self.client_port, self.proc_response)
                self.state = 0

    def send_request(self):
        request = b'\x1b' + 47 * b'\0'
        n = self.ntw.sendUdp4(self.server_addr, self.server_port, request, self.client_port)
        if 0 > n:
            print(f'[SNTP] Fail to send request: error={n}')
        else:
            print('[SNTP] Request sent')
        return n

    def proc_response(self, pkt):
        if 2 != self.state:
            # Ignore unexpected pkt
            return

        self.state = 3
        t = struct.unpack('!12I', pkt.udp_data)[10]
        t -= NTP_EPOCH_DELTA1970

        datetimetuple = time.gmtime(t)
        datetimetuple = (datetimetuple[0] + 1970 - time.gmtime(0)[0],) + datetimetuple[1:]

        print(f'[SNTP] Response received: time={datetimetuple}')
        self.datetimetuple = datetimetuple
        if 0 < self.period:
            print(f'[SNTP] Refresh after {self.period} seconds')

        # Deregister callback for response
        self.ntw.registerUdp4Callback(self.client_port, None)


if __name__ == '__main__':
    # Create network
    nicSpi = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11), miso=Pin(8))
    nicCsPin = Pin(13)
    ntw = Ntw.Ntw(nicSpi, nicCsPin)

    # Set static IP address
    ntw.setIPv4([192,168,40,233], [255,255,255,0], [192,168,40,1])

    # Create SNTP client
    # NTP server address 'pool.ntp.org' is 162.159.200.1
    # Select unused local UDP port: 51000
    sntp_cli = SntpClient(ntw, 51000, [162,159,200,1])

    while True:
        ntw.rxAllPkt()
        sntp_cli.loop()
