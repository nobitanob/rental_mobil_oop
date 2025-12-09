#!/usr/bin/env python3
"""Debug rental code generation"""

from database.connection import DatabaseManager
from models.repositories import PenyewaanRepository

db_manager = DatabaseManager()
penyewaan_repo = PenyewaanRepository(db_manager)

# Get all existing rentals
all_rentals = penyewaan_repo.find_all()
max_seq = 0

print("Existing rentals:")
if all_rentals:
    for r in all_rentals:
        if r.kode_penyewaan:
            print(f"  Code: {r.kode_penyewaan}", end="")
            try:
                parts = r.kode_penyewaan.split('-')
                if len(parts) >= 3:
                    seq_str = parts[-1]
                    seq_num = int(seq_str)
                    print(f" -> seq={seq_num}", end="")
                    if seq_num > max_seq:
                        max_seq = seq_num
                        print(f" (MAX)", end="")
            except Exception as e:
                print(f" -> ERROR: {e}", end="")
            print()

print(f"\nmax_seq = {max_seq}")
print(f"next_seq = {max_seq + 1}")
print(f"Generated code: RENT-202512-{max_seq + 1:04d}")
