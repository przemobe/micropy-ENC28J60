# micropy-ENC28J60 - examples
Examples of using the ENC28J60 Ethernet chip driver for MicroPython.

## List of files
### [Ntw.py](examples/Ntw.py)
This file implements simple IP protocols stack. It contains:
  * ARP for IPv4 over Ethernet, simple ARP table
  * IPv4: reception not fragmented packets, transmission fragmented packets, single IP address
  * ICMPv4: reception Echo Request and transmission Echo Response
  * UDPv4: reception and transmission
  * TCPv4: reception and transmission (protocol states are not supported yet)

### [Dhcp4Client.py](examples/Dhcp4Client.py)
This file implements Dynamic Host Configuration Protocol (DHCP) client for IPv4. It is intended to be used with [Ntw.py](examples/Ntw.py) for automatic IP address configuration.
Refer to  ```if __name__ == '__main__':``` section.

### [PeriodicUdpSender.py](examples/PeriodicUdpSender.py)
This example shows how to use [Ntw.py](examples/Ntw.py) to send UDP datagrams periodically.

### [SntpClient.py](examples/SntpClient.py)
This file implements Simple Network Time Protocol (SNTP) client. It is intended to be used with [Ntw.py](examples/Ntw.py). With that client you can synchronise onboard RTC automatically.
Refer to  ```if __name__ == '__main__':``` section for usage.

### [udpSocket.py](examples/udpSocket.py)
This file implements UDP socket like class. It is intended to be used with [Ntw.py](examples/Ntw.py) and application allows using custom socket (non-system socket). Supports only non-blocking mode.

### [MicrocoapyClient.py](examples/MicrocoapyClient.py)
[microCoAPy](https://github.com/insighio/microCoAPy) client and server example. It is intended to be used with [Ntw.py](examples/Ntw.py) and [udpSocket.py](examples/udpSocket.py).
