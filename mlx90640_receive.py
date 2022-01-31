# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example to display raw packets including header
# Author: Jerry Needell
#
import board
import busio
import digitalio
import adafruit_rfm9x
import time
# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip.
CS = digitalio.DigitalInOut(board.D12)
RESET = digitalio.DigitalInOut(board.D11)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.node=1
# Wait to receive packets.
print("Waiting for packets...")

packet_count = 0
while True:
    # Look for a new packet: only accept if addresses to my_node
    packet = rfm9x.receive(with_ack=True,with_header=True)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        # Print out the raw bytes of the packet:
        # print("Received (raw header):", [hex(x) for x in packet[0:4]])
        # print("Received (raw payload): {0}".format(packet[4:]))
        # print("RSSI: {0}".format(rfm9x.last_rssi))
        # send reading after any packet received
        packet_count += 1
        #print("packet received",packet_count)
        for h in range(4):
            for w in range(32):
                t = packet[4 + h * 32 + w]
                c = "&"
                # pylint: disable=multiple-statements
                if t < 20:
                    c = " "
                elif t < 23:
                    c = "."
                elif t < 25:
                    c = "-"
                elif t < 27:
                    c = "*"
                elif t < 29:
                    c = "+"
                elif t < 31:
                    c = "x"
                elif t < 33:
                    c = "%"
                elif t < 35:
                    c = "#"
                elif t < 37:
                    c = "X"
                # pylint: enable=multiple-statements
                print(c, end="")
            print()

