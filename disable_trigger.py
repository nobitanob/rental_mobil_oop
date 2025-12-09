#!/usr/bin/env python3
"""Disable the problematic trigger"""

from database.connection import DatabaseManager

db_manager = DatabaseManager()

# Drop the trigger
query = "DROP TRIGGER IF EXISTS trg_before_insert_penyewaan"
result = db_manager.execute_query(query)
print(f"Dropped trigger: {result}")
