# micropy-ENC28J60
ENC28J60 Ethernet chip driver for MicroPython v1.17 (RP2)

## Rationale
ENC28J60 is a popular and cheap module for DIY projects.
At the moment, however, there is no driver for the MicroPython environment.
The Python implementation seems easy for further improvements and self adaptation.

## Installation
Copy enc28j60.py to your board into /enc28j60 directory.

## Wiring
Wiring requires pins for SPI: SCK, MISO, MOSI and ChipSelect and Interrupt.
Example wiring that uses SPI1 bus:

| ENC28J60 Module | Rassperry Pi Pico | Notes |
| :-------------: |:-------------:| ---- |
| SCK | GP10 | SPI1 SCK |
| SI | GP11 | SPI1 MOSI/TX |
| SO | GP8 | SPI1 MISO/RX |
| CS | GP13 | SPI1 CSn |
| INT | GP15 | Optional |

## Example Code
To be done...

