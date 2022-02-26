# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example to display raw packets including header
# Author: Jerry Needell
#
import board
import busio
import digitalio
import displayio
import adafruit_rfm9x
import time
import terminalio
import adafruit_ili9341
from adafruit_display_text.label import Label
from simpleio import map_range
import adafruit_mlx90640



# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10

display_bus = displayio.FourWire(
    spi, command=tft_dc, chip_select=tft_cs, reset=board.D6
)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

# Make the display context
splash = displayio.Group()
display.show(splash)

number_of_colors = 64  # Number of color in the gradian
last_color = number_of_colors - 1  # Last color in palette
palette = displayio.Palette(number_of_colors)  # Palette with all our colors

## Heatmap code inspired from: http://www.andrewnoske.com/wiki/Code_-_heatmaps_and_color_gradients
color_A = [
    [0, 0, 0],
    [0, 0, 255],
    [0, 255, 255],
    [0, 255, 0],
    [255, 255, 0],
    [255, 0, 0],
    [255, 255, 255],
]
color_B = [[0, 0, 255], [0, 255, 255], [0, 255, 0], [255, 255, 0], [255, 0, 0]]
color_C = [[0, 0, 0], [255, 255, 255]]
color_D = [[0, 0, 255], [255, 0, 0]]

color = color_B
NUM_COLORS = len(color)


def MakeHeatMapColor():
    for c in range(number_of_colors):
        value = c * (NUM_COLORS - 1) / last_color
        idx1 = int(value)  # Our desired color will be after this index.
        if idx1 == value:  # This is the corner case
            red = color[idx1][0]
            green = color[idx1][1]
            blue = color[idx1][2]
        else:
            idx2 = idx1 + 1  # ... and before this index (inclusive).
            fractBetween = value - idx1  # Distance between the two indexes (0-1).
            red = int(
                round((color[idx2][0] - color[idx1][0]) * fractBetween + color[idx1][0])
            )
            green = int(
                round((color[idx2][1] - color[idx1][1]) * fractBetween + color[idx1][1])
            )
            blue = int(
                round((color[idx2][2] - color[idx1][2]) * fractBetween + color[idx1][2])
            )
        palette[c] = (0x010000 * red) + (0x000100 * green) + (0x000001 * blue)


MakeHeatMapColor()

# Bitmap for colour coded thermal value
image_bitmap = displayio.Bitmap(32, 24, number_of_colors)
# Create a TileGrid using the Bitmap and Palette
image_tile = displayio.TileGrid(image_bitmap, pixel_shader=palette, x=00, y=0)
# Create a Group that scale 32*24 to 128*96
#image_group = displayio.Group(scale=4)
# Create a Group that scale 32*24 to 192*144
image_group = displayio.Group(scale=6)
image_group.append(image_tile)

scale_bitmap = displayio.Bitmap(number_of_colors, 1, number_of_colors)
# Create a Group Scale must be 192 divided by number_of_colors
scale_group = displayio.Group(scale=3)
scale_tile = displayio.TileGrid(scale_bitmap, pixel_shader=palette, x=0, y=55)
scale_group.append(scale_tile)

for i in range(number_of_colors):
    scale_bitmap[i, 0] = i  # Fill the scale with the palette gradian

# Create the super Group
group = displayio.Group()

min_label = Label(terminalio.FONT, color=palette[0], x=0, y=175)
max_label = Label(
    terminalio.FONT,  color=palette[last_color], x=0, y=175
)

# Add all the sub-group to the SuperGroup
group.append(image_group)
group.append(scale_group)
group.append(min_label)
group.append(max_label)

display.show(group)

min_t = 20  # Initial minimum temperature range, before auto scale
max_t = 37  # Initial maximum temperature range, before auto scale

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip.
CS = digitalio.DigitalInOut(board.D12)
RESET = digitalio.DigitalInOut(board.D11)


# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.node=1
# Wait to receive packets.
print("Waiting for packets...")

packet_count = 0
frame = [0] * 768
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
        if packet[4] < 6:
            for h in range(4):
                for w in range(32):
                    t = packet[5 + h * 32 + w] #skip header and packet count
                    frame[128*(packet[4]) + 32*h + w] = t
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
        if(packet[4] == 5):
            mini = frame[0]  # Define a min temperature of current image
            maxi = frame[0]  # Define a max temperature of current image

            for h in range(24):
                for w in range(32):
                    t = frame[h * 32 + w]
                    if t > maxi:
                        maxi = t
                    if t < mini:
                        mini = t
                    image_bitmap[w, (23 - h)] = int(map_range(t, min_t, max_t, 0, last_color))

            min_label.text = "%0.2f" % (min_t)

            max_string = "%0.2f" % (max_t)
            max_label.x = 190 - (5 * len(max_string))  # Tricky calculation to left align
            max_label.text = max_string

            min_t = mini  # Automatically change the color scale
            max_t = maxi
        if packet[4] > 5:
            print(packet)
