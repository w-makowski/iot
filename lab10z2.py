import time, neopixel, board
import RPi.GPIO as GPIO
from config import *
from mfrc522 import MFRC522
from datetime import datetime

execute = True
pixels = neopixel.NeoPixel(board.D8, 8, brightness=1.0/32, auto_write=False)

def button_callback(channel):
    global execute
    execute = False


def beep_buzzer():
    GPIO.output(buzzerPin, 0)
    time.sleep(0.1)
    GPIO.output(buzzerPin, 1)


def show_success_visual():
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(0.5)
    pixels.fill((0, 0, 0))
    pixels.show()


def rfid_read():
    global execute
    MIFAREReader = MFRC522()

    while execute:
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                read_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                num = 0
                for i in range(0, len(uid)):
                    num += uid[i] << (i*8)
                print(f'Card read UID: {uid} > {num}')
                beep_buzzer()
                show_success_visual()
                print(f'Card registered at: {read_time}')
                
                while True:
                    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
                    if status != MIFAREReader.MI_OK:
                        break 
                    time.sleep(0.1)
                
def main():
    try:
        print("Press Ctrl+C to exit.")
        GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback=button_callback, bouncetime=200)

        while True:
            rfid_read()

    except KeyboardInterrupt:
        print("\nExiting program.")

    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
