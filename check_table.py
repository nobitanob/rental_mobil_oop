#!/usr/bin/env python3
"""Check penyewaan table structure"""

from database.connection import DatabaseManager

db_manager = DatabaseManager()

# Check columns
query = "DESCRIBE penyewaan"
results = db_manager.execute_query(query, fetch=True)

print("Penyewaan table structure:")
for row in results:
    print(f"  {row}")

# Check for UNIQUE constraints
print("\nChecking UNIQUE keys:")
query = "SHOW INDEXES FROM penyewaan WHERE Non_unique = 0"
results = db_manager.execute_query(query, fetch=True)
for row in results:
    print(f"  {row}")

# Check triggers
print("\nChecking triggers:")
query = "SHOW TRIGGERS LIKE 'penyewaan%'"
results = db_manager.execute_query(query, fetch=True)
if results:
    for row in results:
        print(f"  {row}")
else:
    print("  No triggers found")
