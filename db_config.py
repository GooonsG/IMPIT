import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='admin',
            database='inventory_database'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
