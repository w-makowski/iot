import RPi.GPIO as GPIO
from mfrc522 import MFRC522
from buzzer import test as buzz
import datetime
import time
from connect_to_db import connect_to_database

class ParkingSystem:
    def __init__(self):
        self.reader = MFRC522()
        self.price_per_hour = 5.5

    def connect_db(self):
        return connect_to_database()

    def check_or_create_user(self, conn, card_id):
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM users WHERE rfid_tag = %s"
            cursor.execute(query, (card_id,)) 
            user = cursor.fetchone()
            
            if not user:
                insert_query = """
                    INSERT INTO users (rfid_tag, name, balance) 
                    VALUES (%s, %s, %s)
                """ 
                cursor.execute(insert_query, (card_id, f"User_{card_id}", 0))
                conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error checking or creating user: {e}")
            return False

    def process_parking_entry(self, conn, card_id, current_time):
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, entry_time, exit_time 
                FROM parking_entries 
                WHERE rfid_tag = %s AND exit_time IS NULL
            """, (card_id,))

            existing_entry = cursor.fetchone()

            if existing_entry:

                cursor.execute("""SELECT bonus_hours FROM bonus_hours WHERE rfid_tag = %s AND timestamp >= ( SELECT entry_time FROM parking_entries 
                    WHERE rfid_tag = %s AND exit_time IS NULL)""", (card_id, card_id))
                bonus_hours = cursor.fetchone()  
                if not bonus_hours:
                    bonus_hours = 0
                total_price, duration = self.calculate_parking_price(existing_entry, bonus_hours)
                cursor.execute("""
                    UPDATE parking_entries 
                    SET exit_time = %s, total_price = %s 
                    WHERE id = %s
                """, (current_time.strftime('%Y-%m-%d %H:%M:%S'), total_price, existing_entry[0]))
                

                self.update_user_balance(conn, card_id, total_price)
                print(f"User {card_id} exited. Duration {duration}. Total price: {total_price:.2f} PLN.")
                conn.commit()
                return "EXIT"
            else:
                cursor.execute("""
                    INSERT INTO parking_entries (rfid_tag, entry_time) 
                    VALUES (%s, %s)
                """, (card_id, current_time.strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                return "ENTRY"
        
        except Exception as e:
            print(f"Error processing parking entry: {e}")
            return "ERROR"


    def calculate_parking_price(self, entry_record, bonus_hours):
        entry_time = datetime.datetime.strptime(entry_record[1], '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        duration = now - entry_time
        hours = max(duration.total_seconds() / 3600 - bonus_hours, 0)
        rounded_hours = int(hours) if hours == int(hours) else int(hours) + 1
        total_price = rounded_hours * self.price_per_hour
        return total_price, duration

    def update_user_balance(self, conn, card_id, amount):
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT balance FROM users WHERE rfid_tag = %s", (card_id,))  
            user = cursor.fetchone()
            
            if user:
                new_balance = user[0] - amount
                cursor.execute("UPDATE users SET balance = %s WHERE rfid_tag = %s", (new_balance, card_id))
                conn.commit()
                print(f"User {card_id} balance updated. New balance: {new_balance:.2f} PLN.")
        except Exception as e:
            print(f"Error updating user balance: {e}")
            raise

    def first_entry_handler(self, conn, card_id):
        print(f"New user registered and entered: {card_id}")

    def entry_handler(self, conn, card_id):
        print(f"User entered: {card_id}")

    def exit_handler(self, conn, card_id):
        print(f"User exited: {card_id}")

    def error_handler(self, error):
        print(f"An error occurred: {error}")

    def run(self):
        try:
            print("System gotowy. Przyłóż kartę.")
            while True:
                status, TagType = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
                if status == self.reader.MI_OK:
                    status, uid = self.reader.MFRC522_Anticoll()
                    if status == self.reader.MI_OK:
                        card_id = "".join([str(x) for x in uid])
                        current_time = datetime.datetime.now()
                        buzz()
                        try:
                            with self.connect_db() as conn:
                                user_created = self.check_or_create_user(conn, card_id)
                                entry_status = self.process_parking_entry(conn, card_id, current_time)

                                if user_created:
                                    self.first_entry_handler(conn, card_id)
                                elif entry_status == "ENTRY":
                                    self.entry_handler(conn, card_id)
                                elif entry_status == "EXIT":
                                    self.exit_handler(conn, card_id)

                        except Exception as e:
                            self.error_handler(e)

        except KeyboardInterrupt:
            print("Program terminated")
        finally:
            GPIO.cleanup()

def main():
    parking_system = ParkingSystem()
    parking_system.run()

if __name__ == "__main__":
    main()
