#!/usr/bin/env python3
"""List available vehicles"""

from database.connection import DatabaseManager
from models.repositories import MobilRepository

db_manager = DatabaseManager()
mobil_repo = MobilRepository(db_manager)

available = mobil_repo.find_available()
print(f"Available vehicles ({len(available)}):")
for m in available:
    print(f"  ID {m.id}: {m.merk} {m.model} - Rp {m.harga_sewa_per_hari:,}/day")
