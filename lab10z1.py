#!/usr/bin/env python3

from config import *
import time, os, board, neopixel, w1thermsensor, busio
import adafruit_bme280.advanced as adafruit_bme280
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
disp = SSD1331.SSD1331()

def bme280_setup():
    bme280.sea_level_pressure = 1013.25
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16


def display(temperature, humidity, pressure):
    image = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image)

    font_small = ImageFont.truetype('/lib/oled/Font.tth', 10)

    image_temp = Image.open('./pictures/temperature.jpg')
    image_temp = image_temp.resize((15, 10))
    image_hum = Image.open('./pictures/humidity.jpg')
    image_hum = image_temp.resize((15, 10))
    image_pres = Image.open('./pictures/pressure.jpg')
    image_pres = image_temp.resize((15, 10))

    image.paste(image_temp, (0, 0))
    draw.text((20, 0), f'Temperature: {temperature}', font=font_small, fill="BLACK")

    image.paste(image_hum, (0, 25))
    draw.text((20, 25), f'Humidity: {humidity}', font=font_small, fill="BLACK")

    image.paste(image_pres, (0, 50))
    draw.text((20, 50), f'Pressure: {pressure}', font=font_small, fill="BLACK")

    disp.ShowImage(image, 0, 0)


def read_bme280():
    bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2
    return bme280.temperature, bme280.humidity, bme280.pressure


def main():
    try:
        print("Press Ctrl+C to exit.")
        bme280_setup()
        disp.Init()

        while True:
            temp, hum, pres = read_bme280()
            display(temp, hum, pres)

    except KeyboardInterrupt:
        print("\nExiting program.")

    finally:
        GPIO.cleanup()

if __name__ == "__main__"
    main()
    