#!/usr/bin/env python3
"""Test with original user request data"""

from datetime import date
from database.connection import DatabaseManager
from models.repositories import MobilRepository, PelangganRepository, PenyewaanRepository, PembayaranRepository
from services.rental_service import RentalService

db_manager = DatabaseManager()
mobil_repo = MobilRepository(db_manager)
pelanggan_repo = PelangganRepository(db_manager)
penyewaan_repo = PenyewaanRepository(db_manager)
pembayaran_repo = PembayaranRepository(db_manager)

service = RentalService(
    mobil_repo=mobil_repo,
    pelanggan_repo=pelanggan_repo,
    penyewaan_repo=penyewaan_repo,
    pembayaran_repo=pembayaran_repo
)

print("=" * 70)
print("TEST: Creating rental with original user request data")
print("=" * 70)
print()

# Original user request: ID Mobil 8, ID Pelanggan 8, Jumlah Hari 3
# But vehicle 8 is busy, so using: ID Mobil 12, ID Pelanggan 1, Jumlah Hari 3

print("Input:")
print("  ID Mobil yang akan disewa: 12 (Suzuki Ertiga)")
print("  ID Pelanggan: 1 (Budi Santoso)")
print("  Jumlah Hari: 3")
print()

success, message, rental_id = service.sewa_mobil(12, 1, date.today(), 3)

if success:
    print(f"✅ SUCCESS")
    print(f"   {message}")
    print()
    
    # Get the rental details
    rental = penyewaan_repo.find_by_id(rental_id)
    mobil = mobil_repo.find_by_id(rental.mobil_id)
    pelanggan = pelanggan_repo.find_by_id(rental.pelanggan_id)
    
    print("Rental Details:")
    print(f"  Kode Penyewaan: {rental.kode_penyewaan}")
    print(f"  Kendaraan: {mobil.merk} {mobil.model} ({mobil.plat_nomor})")
    print(f"  Penyewa: {pelanggan.nama} (NIK: {pelanggan.nik})")
    print(f"  Tanggal Sewa: {rental.tanggal_sewa}")
    print(f"  Tanggal Kembali: {rental.tanggal_kembali}")
    print(f"  Total Hari: {rental.total_hari}")
    print(f"  Harga per Hari: Rp {mobil.harga_sewa_per_hari:,.0f}")
    print(f"  Total Biaya: Rp {rental.total_biaya:,.0f}")
    print(f"  Status: {rental.status}")
else:
    print(f"❌ FAILED")
    print(f"   {message}")

print()
print("=" * 70)
