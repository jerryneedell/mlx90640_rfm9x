# mlx90640_rfm9x
Transmit mlx90604 image via rfm9x to receiver for display

* mlx90640_radio_pico.py -- transmitter for PAsberry Pi Pico
* mlx90640_radio_feather_rp2040.py -- transmitter for feather_rp2040
* mlx90600_receive.py -- basic receive for feather rp2040 -- ascii art display
* mlx90640_receive_tft24.py - receiver for feahter rp2040 with 2.4inch tft -- image display
* mlx90640_simpletest.py  -- basic demo code for mlx90640 on Raspberry Pi Pico
* mlx_tft24.py  -- demo code for 2.4 inch TFT on a feather rp2040 with mlx90640

The transmit program breaks each mlx90640 image into 6 packets of 128 bytes and prepends a byte indicating the index of the packet into the image. THe index byte will be from 0 to 5. When a packet with index 5 has arrive, then the image is complete.

