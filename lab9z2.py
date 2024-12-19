#!/usr/bin/env python3

from config import *
import time, os, board, neopixel, w1thermsensor, busio
import adafruit_bme280.advanced as adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)

mode = 0


def bme280_setup():
    bme280.sea_level_pressure = 1013.25
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16


def bme280_scan():
    bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2


def button_callback(channel):
    global mode
    mode = (mode + 1) % 3


def set_pixels_color_and_leds(parameter, low, high):
    if parameter < low:
        color = (0, 0, 255)
        # num_leds = min(int((parameter / low) * 3), 3)
    elif parameter > high:
        color = (255, 0, 0)
        # num_leds = 8
    else:
        color = (0, 255, 0)
        # num_leds = max(min(int(((parameter - low) / (high - low)) * 6), 6), 3)

    for i in range(8):
        if i < num_leds:
            pixels[i] = color
        else:
            pixels[i] = (0, 0, 0)
    pixels.show()


def update_pixels():
    temperature, humidity, pressure = get_sensor_values()

    print(f"Temperature: {temperature:.2f} °C, Humidity: {humidity:.2f} %, Pressure: {pressure:.2f} hPa")

    if mode == 0:
        set_pixels_color_and_leds(temperature, 10, 25)
    elif mode == 1:
        set_pixels_color_and_leds(humidity, 30, 60)
    elif mode == 2:
        set_pixels_color_and_leds(pressure, 980, 1020)



def main():
    try:
        print("Press Ctrl+C to exit.")
        bme280_setup()
        GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback=button_callback, bouncetime=200)

        while True:
            update_pixels()

    except KeyboardInterrupt:
        print("\nExiting program.")

    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
