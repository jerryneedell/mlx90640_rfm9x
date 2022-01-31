import time
import board
import busio
import adafruit_mlx90640
import digitalio
import adafruit_rfm9x


# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D10)
RESET = digitalio.DigitalInOut(board.D11)
# Or uncomment and instead use these if using a Feather M0 RFM9x board and the appropriate
# CircuitPython build:
# CS = digitalio.DigitalInOut(board.RFM9X_CS)
# RESET = digitalio.DigitalInOut(board.RFM9X_RST)


# Initialize SPI bus.
spi = board.SPI()

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23
rfm9x.node = 2
rfm9x.destination = 1

i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)

mlx = adafruit_mlx90640.MLX90640(i2c)
print("MLX addr detected on I2C")
print([hex(i) for i in mlx.serial_number])

mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

frame = [0] * 768
byte_frame = bytearray(768)
packet = bytearray(129)
while True:
    try:
        mlx.getFrame(frame)
        for i in range(len(frame)):
            byte_frame[i] = int(frame[i])
    except ValueError:
        # these happen, no biggie - retry
        continue
    for i in range(6):
        packet[0] = i
        packet[1:]=byte_frame[i*128:(i+1)*128]
        print("sending packet",i)
        if not rfm9x.send_with_ack(bytes(packet)):
            print("no ack: ",i)
    time.sleep(5)

