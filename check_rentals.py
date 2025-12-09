#!/usr/bin/env python3
"""Check existing rentals"""

from database.connection import DatabaseManager
from models.repositories import PenyewaanRepository

db_manager = DatabaseManager()
penyewaan_repo = PenyewaanRepository(db_manager)

all_rentals = penyewaan_repo.find_all()
print(f"Total rentals: {len(all_rentals)}")
for r in all_rentals:
    print(f"  ID: {r.id}, Code: {r.kode_penyewaan}, Status: {r.status}")
