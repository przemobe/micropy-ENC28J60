# micropy-ENC28J60
ENC28J60 Ethernet chip driver for MicroPython v1.17 (RP2)

## Rationale
ENC28J60 is a popular and cheap module for DIY projects.
At the moment, however, there is no driver for the MicroPython environment.
The Python implementation seems easy for further improvements and self adaptation.

## Installation
Copy enc28j60.py to your board into /enc28j60 directory.

## Wiring
Wiring requires pins for SPI: SCK, MISO, MOSI and ChipSelect and optionally Interrupt.
Example wiring that uses SPI1 bus:

| ENC28J60 Module | Rassperry Pi Pico | Notes |
| :-------------: |:-------------:| ---- |
| VCC | 3V3 | requires up to 180 mA |
| GND | GND | |
| SCK | GP10 | SPI1 SCK |
| SI | GP11 | SPI1 MOSI/TX |
| SO | GP8 | SPI1 MISO/RX |
| CS | GP13 | SPI1 CSn |
| INT | GP15 | Optional |

## To do
 - interrupt handler


## Example code

### Packet transmission
Example of packet transmission to broadcast ethernet address:

```python
from machine import Pin, SPI
from enc28j60 import enc28j60

spi1 = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11), miso=Pin(8))
eth = enc28j60.ENC28J60(spi1, Pin(13))
eth.init()

srcMac = eth.getMacAddr()
tgtMac = bytearray([0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
payLoad = bytearray(64)
pktType = bytearray([(len(payLoad) >> 8) & 0xFF, len(payLoad) & 0xFF])

eth.SendPacket([tgtMac, srcMac, pktType, payLoad])
```

### Packet reception
Example of packet reception:

```python
from machine import Pin, SPI
from enc28j60 import enc28j60

spi1 = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11), miso=Pin(8))
eth = enc28j60.ENC28J60(spi1, Pin(13))
eth.init()

print("myMac:", ":".join("{:02x}".format(c) for c in eth.getMacAddr()))
print("ENC28J60 revision ID: 0x{:02x}".format(eth.GetRevId()))

pkt = bytearray()

while eth.GetRxPacketCnt():
	eth.ReceivePacket(pkt)
	print('srcMac:', ":".join("{:02x}".format(c) for c in pkt[6:12]))
```
