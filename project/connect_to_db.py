import mysql.connector

# Funkcja do połączenia z bazą danych
def connect_to_database(host='10.108.33.111', user='tescik', password='aha', database='parking'):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        raise
