#!/usr/bin/env python
# -*- coding: utf8 -*-

# Copyright 2021-2022 Przemyslaw Bereski https://github.com/przemobe/

from machine import Pin
from machine import SPI
import Ntw
import time


class PeriodicSender:
    def __init__(self, ntw, tgt_addr, tgt_port, period_sec):
        self.ntw = ntw
        self.tgt_addr = bytes(tgt_addr)
        self.tgt_port = tgt_port
        self.period_sec = period_sec
        self.state = 0
        self.init_time = 0

    def loop(self):
        ctime = time.time()

        if 0 == self.state:
            if not ntw.isIPv4Configured():
                return
            print('Connecting...')
            ntw.connectIp4(self.tgt_addr)
            self.init_time = ctime
            self.state = 1

        elif 1 == self.state:
            if ntw.isConnectedIp4(self.tgt_addr):
                print('Connected')
                self.init_time = ctime
                self.state = 2
                self.send_data()
            elif ctime - self.init_time > 3:
                self.state = 0

        else: # 2 == self.state
            if ctime - self.init_time > self.period_sec:
                self.send_data()
                self.init_time += self.period_sec

    def send_data(self):
        n = self.ntw.sendUdp4(self.tgt_addr, self.tgt_port, '<134>I am alive!'.encode())
        if 0 > n:
            print(f'Fail to send data error={n}')
        else:
            print('Data sent')


if __name__ == '__main__':
    # Create network
    nicSpi = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11), miso=Pin(8))
    nicCsPin = Pin(13)
    ntw = Ntw.Ntw(nicSpi, nicCsPin)

    # Set static IP address
    ntw.setIPv4([192,168,40,233], [255,255,255,0], [192,168,40,1])

    # Create periodic sender
    sender = PeriodicSender(ntw, [192,168,40,129], 514, 60)

    while True:
        ntw.rxAllPkt()
        sender.loop()
