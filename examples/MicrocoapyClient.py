#!/usr/bin/env python
# -*- coding: utf8 -*-

#   Copyright 2023 Przemyslaw Bereski https://github.com/przemobe/

#   MicroPython RP2
#   ENC28J60 (https://github.com/przemobe/micropy-ENC28J60) and
#   microCoAPy (https://github.com/insighio/microCoAPy) integration.

#   CoAP client and server example.

import Ntw
from machine import Pin
from machine import SPI

try:
    import Dhcp4Client
except ImportError:
    Dhcp4Client = None

import microcoapy
from udpSocket import UdpSocket
import time


def receivedMessageCallback(packet, sender):
    print(f'[CoAP] Message received: {packet.toString()}, format: {packet.content_format}, from: {sender}')
    if packet.payload is not None:
        try:
            print(f'[CoAP] Message payload: {packet.payload.decode("unicode_escape")}')
        except Exception as e:
            print(f'[CoAP] Exception: {e}')


def testRequestCallback(packet, senderIp, senderPort):
    print(f'[CoAP] Test request received: {packet.toString()} from: {senderIp}:{senderPort}')
    coap.sendResponse(senderIp, senderPort, packet.messageid, 'This is test message response from ENC28J60 RP2.',
        microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT, microcoapy.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN, packet.token)


def discoveryRequestCallback(packet, senderIp, senderPort):
    print(f'[CoAP] "well-known/core" received: {packet.toString()} from: {senderIp}:{senderPort}')
    response = b'</test>;rt="test";ct=0'
    coap.sendResponse(senderIp, senderPort, packet.messageid, response,
        microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT, microcoapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)


if __name__ == "__main__":
    # Create network
    nicSpi = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11), miso=Pin(8))
    nicCsPin = Pin(13)
    ntw = Ntw.Ntw(nicSpi, nicCsPin)

    # Setup network IP layer
    dhcp_client = None
    if Dhcp4Client is None:
        # Set static IP address
        ntw.setIPv4([192,168,40,233], [255,255,255,0], [192,168,40,1])
    else:
        # Create DHCP client
        dhcp_client = Dhcp4Client.Dhcp4Client(ntw)

    # Setup CoAP
    remoteServerIpStr = "134.102.218.18"
    remoteServerPort = 5683
    remoteServerIpBytes = bytes([int(x) for x in remoteServerIpStr.split('.')])

    coap = microcoapy.Coap()
    coap.responseCallback = receivedMessageCallback
    coap.addIncomingRequestCallback('test', testRequestCallback)
    coap.addIncomingRequestCallback('.well-known/core', discoveryRequestCallback)

    coapSocket = UdpSocket(ntw, microcoapy.coap_macros._COAP_DEFAULT_PORT)
    #coapSocket.debug = True
    coap.setCustomSocket(coapSocket)

    coapClient_startTime = time.time()
    coapClient_doneFlag = False

    # Main loop
    while True:
        ntw.rxAllPkt()
        if dhcp_client is not None:
            dhcp_client.loop()

        coap.loop(False)

        # CoAP client - send one time request(s) to remote server after start
        ctime = time.time()
        if (False == coapClient_doneFlag) and (ctime - coapClient_startTime > 1) and (ntw.isIPv4Configured()):
            startTime = ctime
            if not ntw.isConnectedIp4(remoteServerIpBytes):
                ntw.connectIp4(remoteServerIpBytes)
            else:
                #coap.get(remoteServerIpStr, remoteServerPort, '.well-known/core')
                #coap.get(remoteServerIpStr, remoteServerPort, 'test')
                coap.get(remoteServerIpStr, remoteServerPort, 'separate')
                coapClient_doneFlag = True
