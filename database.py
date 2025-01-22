import sqlite3

DB_FILE = "parking.db"

def initialize_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT NOT NULL,
        entry_time TEXT NOT NULL,
        exit_time TEXT,
        discount_used INTEGER DEFAULT 0,
        status TEXT DEFAULT 'entered'
    )
    """)
    connection.commit()
    connection.close()

def add_entry(uid, entry_time):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO sessions (uid, entry_time) VALUES (?, ?)", (uid, entry_time))
    connection.commit()
    connection.close()

def handle_exit(uid):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT entry_time, discount_used FROM sessions WHERE uid = ? AND status = 'entered'", (uid,))
    result = cursor.fetchone()
    connection.close()
    return result

def update_discount(uid, discount_hours):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("UPDATE sessions SET discount_hours = ? WHERE uid = ? AND status = 'entered'", (discount_hours, uid))
    connection.commit()
    connection.close()

def update_exit(uid, exit_time):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("UPDATE sessions SET exit_time = ?, status = 'completed' WHERE uid = ? AND status = 'entered'",
    (exit_time, uid))
    connection.commit()
    connection.close()

def validate_entry(uid):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT status FROM sessions WHERE uid = ? AND status = 'entered'", (uid,))
    result = cursor.fetchone()
    connection.close()
    if result:
        return False

    return True

def validate_discount(uid):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT discount_used FROM sessions WHERE uid = ? AND status = 'entered' AND discount_used <> 0", (uid,))
    result = cursor.fetchone()
    connection.close()
    if result:
        return False

    return True

def validate_exit(uid):
    connection = sqlite3.connect("parking.db")
    cursor = connection.cursor()
    cursor.execute("SELECT status FROM parking_sessions WHERE uid = ? AND status = 'entered'", (uid,))
    result = cursor.fetchone()
    connection.close()
    
    if not result:
        return False
    
    return True

