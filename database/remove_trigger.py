#!/usr/bin/env python3
"""Remove the problematic before-insert trigger permanently"""

import mysql.connector
from mysql.connector import Error

config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'rental_mobil_db'
}

try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    print("Removing problematic trigger: trg_before_insert_penyewaan")
    cursor.execute("DROP TRIGGER IF EXISTS trg_before_insert_penyewaan")
    connection.commit()
    print("✓ Trigger removed successfully")
    
except Error as e:
    print(f"✗ Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
