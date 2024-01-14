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

from uDnsClient import DnsClientNtw, DNS_RCODE_NOERROR
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

def ledToggleCallback(packet, senderIp, senderPort):
    print(f'[CoAP] LED toggle received: {packet.toString()} from: {senderIp}:{senderPort}')
    ledPin.toggle()
    coap.sendResponse(senderIp, senderPort, packet.messageid, f'LED status: {ledPin.value()}.',
        microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT, microcoapy.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN, packet.token)

def discoveryRequestCallback(packet, senderIp, senderPort):
    print(f'[CoAP] "well-known/core" received: {packet.toString()} from: {senderIp}:{senderPort}')
    response = b'</test>;rt="test";ct=0,</ledToggle>;rt="ledToggle";ct=0'
    coap.sendResponse(senderIp, senderPort, packet.messageid, response,
        microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT, microcoapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)


def dnsCallback(hostname, status, addr, ttl):
    if DNS_RCODE_NOERROR != status or addr is None:
        print(f'[DNS] Cannot resolve {hostname} name')
        return

    global remoteServerIp
    remoteServerIp = addr
    print(f'[DNS] {hostname} at {addr[0]}.{addr[1]}.{addr[2]}.{addr[3]}')


if __name__ == "__main__":
    # LED pin
    ledPin = Pin(25, Pin.OUT)
    ledPin.value(1)

    # Create network
    nicSpi = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11), miso=Pin(8))
    nicCsPin = Pin(13)
    ntw = Ntw.Ntw(nicSpi, nicCsPin)

    # Setup DNS client
    dns_client = DnsClientNtw(ntw, 56789)

    # Setup network IP layer
    dhcp_client = None
    if Dhcp4Client is None:
        # Set static IP address
        ntw.setIPv4([192,168,40,233], [255,255,255,0], [192,168,40,1])
        dns_client.set_serv_addr(bytes([8,8,8,8]))
    else:
        # Create DHCP client
        dhcp_client = Dhcp4Client.Dhcp4Client(ntw)


    # Setup CoAP
    global remoteServerIp
    remoteServerIp = None
    remoteServerName = 'coap.me'
    dns_client.resolve_host_name(remoteServerName, callback=dnsCallback)
    remoteServerPort = microcoapy.coap_macros._COAP_DEFAULT_PORT #5683

    coap = microcoapy.Coap()
    coap.responseCallback = receivedMessageCallback
    coap.addIncomingRequestCallback('test', testRequestCallback)
    coap.addIncomingRequestCallback('ledToggle', ledToggleCallback)
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

        dns_client.loop()
        coap.loop(False)

        # CoAP client - send one time request(s) to remote server after start
        ctime = time.time()
        if not dns_client.is_serv_addr_set() and ntw.isIPv4Configured():
            dns_client.set_serv_addr(ntw.getDnsSrvIpv4())

        if (False == coapClient_doneFlag) and (ctime - coapClient_startTime > 1) and ntw.isIPv4Configured() and (remoteServerIp is not None):
            startTime = ctime
            if not ntw.isConnectedIp4(remoteServerIp):
                ntw.connectIp4(remoteServerIp)
            else:
                #coap.get(remoteServerIp, remoteServerPort, '.well-known/core')
                #coap.get(remoteServerIp, remoteServerPort, 'test')
                coap.get(remoteServerIp, remoteServerPort, 'separate')
                coapClient_doneFlag = True
