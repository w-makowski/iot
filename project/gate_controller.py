#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
import datetime
from config import *
import paho.mqtt.client as mqtt
from buzzer import test as buzz
from mfrc522 import MFRC522

from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331
import board
import busio
import adafruit_bme280.advanced as adafruit_bme280

broker = "10.108.33.123" # IP centralnego serwera (MQTT broker)
topic_entry = "parking/entry"
topic_exit = "parking/exit"
topic_entry_response = "parking/entry_response"
topic_exit_response = "parking/exit_response"
PRICE_PER_H = 4

client = mqtt.Client()


disp = SSD1331.SSD1331()
disp.Init()
disp.clear()
image = Image.new("RGB", (disp.width, disp.height), "WHITE")
draw = ImageDraw.Draw(image)
fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', 13)


def display_message(line1, line2=None):
    draw.rectangle([(0, 0), (disp.width, disp.height)], fill="WHITE")
    draw.text((5, 5), line1, font=fontSmall, fill="BLACK")
    if line2:
        draw.text((5, 25), line2, font=fontSmall, fill="BLACK")
    disp.ShowImage(image, 0, 0)


def rfid_read(entry_mode=True):
    reader = MFRC522()

    while True:
        status, _ = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status == reader.MI_OK:
            status, uid = reader.MFRC522_Anticoll()
            if status == reader.MI_OK:
                card_id = "".join([str(x) for x in uid])
                current_time = datetime.datetime.now()
                buzz()
                if entry_mode:
                    call_worker(topic_entry, card_id, current_time)
                else:
                    call_worker(topic_exit, card_id, current_time)
                while status == reader.MI_OK:
                    status, _ = reader.MFRC522_Anticoll()


def call_worker(topic, card, read_time):
    client.publish(topic, str(card) + "#" + str(read_time),)


def on_message(client, userdata, message):
    topic = message.topic
    message_decoded = (str(message.payload.decode("utf-8"))).split("#")

    if topic == topic_entry_response:
        uid, response = message_decoded
        if response == "OK":
            display_message("Wjazd zaakceptowany")
        else:
            display_message("Wjazd odrzucony")
    elif topic == topic_exit_response:
        uid, response, total_time, discount_hours, chargeable_hours = message_decoded
        if response == "OK":
            print(f"Wyjazd zaakceptowany. Czas: {total_time}h, Zniżka: {discount_hours}h, Do zapłaty: {chargeable_hours} PLN")
            display_message(f"Wyjazd zaakceptowany", 
                            f"Do zapłaty: {int(chargeable_hours) * PRICE_PER_H} PLN")
        else:
            print("Wyjazd odrzucony")


def connect_to_broker():
    client.connect(broker)
    call_worker("Client connected", datetime.datetime.now())
    client.subscribe([(topic_entry_response, 0), (topic_exit_response, 0)])
    client.on_message = on_message
    client.loop_start()


# def connect_to_broker():
#     client.connect(broker)
#     call_worker("Client connected", datetime.datetime.now())

def disconnect_from_broker():
    call_worker("Client disconnected", datetime.datetime.now())
    client.disconnect()


def run_gate_controller():
    connect_to_broker()
    rfid_read()
    disconnect_from_broker()


if __name__ == "__main__":
    run_gate_controller()
