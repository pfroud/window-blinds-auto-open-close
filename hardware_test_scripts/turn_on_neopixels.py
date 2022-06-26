# test for addressable RGB LEDs
import os
import board
import neopixel


def main():
    pixels = neopixel.NeoPixel(
        board.D21, 35, brightness=1.0, auto_write=True, pixel_order=neopixel.GRB
    )
    pixels.fill((1, 1, 1))  # RGB out of 255


if __name__ == '__main__':
    if os.geteuid() == 0:
        main()
    else:
        exit(__file__ + ": Need to run the script as root (use sudo) to access GPIO.")
