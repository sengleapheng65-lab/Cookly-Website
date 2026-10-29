# backend/db.py
# backend/db.py
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="Bunrady@123456",  # Use "" if root has no password
            database="cookly_db"
        )
        return connection
    except Error as e:
        print(f"MySQL Connection Error: {e}")
        return None