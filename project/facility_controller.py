#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
import datetime
from config import *
import paho.mqtt.client as mqtt
from buzzer import test as buzz
from mfrc522 import MFRC522

broker = "10.108.33.123" # IP centralnego serwera (MQTT broker)
topic_discount = "parking/discount"
DISCOUNT_HOURS = 2

client = mqtt.Client()

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

                # czy znizka bedzie liczona od czasu odbicia przy szlabanie czy tego tutaj??
                call_worker(topic_discount, card_id, current_time) 

                while status == reader.MI_OK:
                    status, _ = reader.MFRC522_Anticoll()


def call_worker(topic, card, read_time):
    client.publish(topic, str(card) + "#" + str(read_time),)


def connect_to_broker():
    client.connect(broker)
    call_worker("Client connected", datetime.datetime.now())


def disconnect_from_broker():
    call_worker("Client disconnected", datetime.datetime.now())
    client.disconnect()


def run_gate_controller():
    connect_to_broker()
    rfid_read()
    disconnect_from_broker()


if __name__ == "__main__":
    run_gate_controller()

