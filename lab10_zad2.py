import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import datetime
from buzzer import test as buzz

reader = MFRC522()

try:
    print("System gotowy. Przyłóż kartę.")
    while True:
        status, TagType = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status == reader.MI_OK:
            status, uid = reader.MFRC522_Anticoll()
            if status == reader.MI_OK:
                card_id = "".join([str(x) for x in uid])
                current_time = datetime.datetime.now()
                buzz()
                print(f'{card_id} - {current_time}')
                while status == reader.MI_OK:
                    status, _ = reader.MFRC522_Anticoll()

except KeyboardInterrupt:
    print("Program przerwany.")
finally:
    GPIO.cleanup()