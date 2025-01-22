#!/usr/bin/env python3

import time
import datetime
from config import *
import paho.mqtt.client as mqtt
import database

STATUS_OK = "OK"
STATUS_DENIED = "DENIED"

broker = "10.108.33.122" # IP centralnego serwera (MQTT broker) lub localhost?
topics = {
    "entry_request": "parking/entry_request",
    "entry_response": "parking/entry_response",
    "exit_request": "parking/exit_request",
    "exit_response": "parking/exit_response",
    "discount_request": "parking/discount_request",
    "discount_response": "parking/discount_response",
}

client = mqtt.Client()


def handle_entry(uid, entry_time):
    if database.validate_entry(uid):
        database.add_entry(uid, entry_time)
        return STATUS_OK
    return STATUS_DENIED


def handle_exit(uid, exit_time):
    if database.validate_exit(uid):
        entry_time, discount_hours = database.handle_exit(uid)
        total_time = datetime.datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
        chargeable_hours = max(total_time.total_seconds() / 3600 - discount_hours, 0)
        database.update_exit(uid, exit_time)
        return f"OK#{total_time.total_seconds() / 3600:.2f}#{discount_hours}#{chargeable_hours:.2f}"
    return STATUS_DENIED


def handle_discount(uid, discount_hours):
    if database.validate_discount(uid):
        database.update_discount(uid, discount_hours)
        return STATUS_OK
    return STATUS_DENIED


def on_message(client, userdata, message):
    topic = message.topic
    message_decoded = (str(message.payload.decode("utf-8"))).split("#")

    uid = message_decoded[0]
    response = ""
    if topic == topics["entry_request"]:
        response = handle_entry(uid, message_decoded[1])
        client.publish(topics["entry_response"], f"{uid}#{response}")
    elif topic == topics["exit_request"]:
        response = handle_exit(uid, message_decoded[1])
        client.publish(topics["exit_response"], f"{uid}#{response}")
    elif topic == topics["discount_request"]:
        response = handle_discount(uid, int(message_decoded[1]))
        # tutaj chyba nie potrzebna jest informacja zwrotna:
        # client.publish(topics["discount_response"], f"{uid}#{response}")
    

def connect_to_broker():
    client.connect(broker)
    client.on_message = on_message
    client.loop_start()
    client.subscribe([(topics["entry_request"], 0), (topics["exit_request"], 0), (topics["discount_request"], 0)])
    print("MQTT handler running.")


def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()


def run_receiver():
    connect_to_broker()
    try:
        while True:
            time.sleep(1)
        except KeyboardInterrupt:
            print("exiting")
        disconnect_from_broker()


if __name__ == "__main__":
    run_receiver()
