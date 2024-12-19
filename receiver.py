#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import sqlite3, time


broker = "localhost"
client = mqtt.Client()


def process_message(client, userdata, message):
    message_decoded = (str(message.payload.decode("utf-8"))).split(":")

    if message_decoded[0] != "Client connected" and message_decoded != "Client disconnected":
        print(time.ctime() + ", " + message_decoded[0] + " used the RFID card.")

        connection = sqlite3.connect("workers.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO workers_log VALUES (?,?,?)", (time.ctime(), message_decoded[0], message_decoded[1]))
        connection.commit()
        connection.close()
    else:
        print(message_decoded[0] + ": " + message_decoded[1])


def connect_to_broker():
    client.connect(broker)
    client.on_message = process_message
    client.loop_start()
    client.subscribe("worker/name")
    while client.loop() == 0:
        pass


def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()


def run_receiver():
    connect_to_broker()
    disconnect_from_broker()


if __name__ == "__main__":
    run_receiver()
