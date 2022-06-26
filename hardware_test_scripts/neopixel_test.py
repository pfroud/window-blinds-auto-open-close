# Simple test for NeoPixels on Raspberry Pi
# From https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage
import os
import time
import board
import neopixel


# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D21

# The number of NeoPixels
num_pixels = 35

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)


def main():
    print("Press Ctrl+C to stop")
    while True:
        pixels.fill((100, 0, 0))
        pixels.show()
        time.sleep(1.0)

        pixels.fill((0, 100, 0))
        pixels.show()
        time.sleep(1.0)

        pixels.fill((0, 0, 100))
        pixels.show()
        time.sleep(1.0)

        rainbow_cycle(0.01)  # rainbow cycle with 1ms delay per step


if __name__ == '__main__':
    if os.geteuid() == 0:
        main()
    else:
        exit(__file__ + ": Need to run the script as root (use sudo) to access GPIO.")
