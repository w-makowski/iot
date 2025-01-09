#!/usr/bin/env python3
import time
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331
import board
import busio
import adafruit_bme280.advanced as adafruit_bme280



def resize_icon(input_path, output_path, size):
     with Image.open(input_path) as img:
        img = img.convert("RGBA") 
        img = img.resize(size, Image.ANTIALIAS)
        img.save(output_path, format="PNG")


resize_icon('humidity_icon.jpg', 'humidity_icon_resized.jpg', (13, 13))
resize_icon('pressure_icon.jpg', 'pressure_icon_resized.jpg', (13, 13))
resize_icon('temperature_icon.jpg', 'temperature_icon_resized.jpg', (13, 13))

icon_temp = Image.open('/home/pi/tests/temperature_icon_resized.jpg').convert("RGBA")
icon_humidity = Image.open('/home/pi/tests/humidity_icon_resized.jpg').convert("RGBA")
icon_pressure = Image.open('/home/pi/tests/pressure_icon_resized.jpg').convert("RGBA")



def oledtest():
    disp = SSD1331.SSD1331()

    disp.Init()
    disp.clear()

    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    fontLarge = ImageFont.truetype('./lib/oled/Font.ttf', 20)
    fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', 13)

    while True:
        temperature = bme280.temperature  # Temperatura w °C
        humidity = bme280.humidity        # Wilgotność w %
        pressure = bme280.pressure        # Ciśnienie w hPa

        # Czyszczenie obrazu
        draw.rectangle([(0, 0), (disp.width, disp.height)], fill="WHITE")

        print(temperature)

        image1.paste(icon_temp, (10, 0), icon_temp)
        image1.paste(icon_humidity, (10, 20), icon_humidity)
        image1.paste(icon_pressure, (10, 40), icon_pressure)
       
        draw.text((25, 0), f"{temperature:.1f}°C", font=fontSmall, fill="BLACK")
        draw.text((25, 20), f"{humidity:.1f}%", font=fontSmall, fill="BLACK")
        draw.text((25, 40), f"{pressure:.1f} hPa", font=fontSmall, fill="BLACK")


        disp.ShowImage(image1, 0, 0)

        time.sleep(2)

def test():
    print('\nTest wyświetlacza OLED z czujnikiem BME280.')
    oledtest()

if __name__ == "__main__":
    test()
