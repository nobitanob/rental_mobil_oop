#!/usr/bin/env python3
"""Test complete rental creation workflow"""

from datetime import date
from database.connection import DatabaseManager
from models.repositories import MobilRepository, PelangganRepository, PenyewaanRepository, PembayaranRepository
from services.rental_service import RentalService

def test_full_workflow():
    """Test the complete rental workflow"""
    
    # Initialize database manager and repositories
    db_manager = DatabaseManager()
    mobil_repo = MobilRepository(db_manager)
    pelanggan_repo = PelangganRepository(db_manager)
    penyewaan_repo = PenyewaanRepository(db_manager)
    pembayaran_repo = PembayaranRepository(db_manager)
    
    # Create rental service
    service = RentalService(
        mobil_repo=mobil_repo,
        pelanggan_repo=pelanggan_repo,
        penyewaan_repo=penyewaan_repo,
        pembayaran_repo=pembayaran_repo
    )
    
    print("=" * 60)
    print("RENTAL MOBIL - WORKFLOW TEST")
    print("=" * 60)
    
    # Test case 1: Original user request
    print("\n[Test 1] Rental dengan ID Mobil 8, ID Pelanggan 8, Durasi 3 hari")
    print("-" * 60)
    
    success, message, rental_id = service.sewa_mobil(8, 8, date.today(), 3)
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
    
    # Test case 2: Another rental to test sequence counter
    print("\n[Test 2] Rental dengan ID Mobil 5, ID Pelanggan 3, Durasi 2 hari")
    print("-" * 60)
    
    success, message, rental_id = service.sewa_mobil(5, 3, date.today(), 2)
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
    
    # Show all rentals
    print("\n[Summary] Semua Penyewaan dalam Sistem")
    print("-" * 60)
    
    all_rentals = penyewaan_repo.find_all()
    for r in all_rentals:
        mobil = mobil_repo.find_by_id(r.mobil_id)
        pelanggan = pelanggan_repo.find_by_id(r.pelanggan_id)
        print(f"Kode: {r.kode_penyewaan:15} | {mobil.merk} {mobil.model:15} | "
              f"{pelanggan.nama:20} | Rp {r.total_biaya:10,.0f} | Status: {r.status:10}")
    
    print("\n" + "=" * 60)
    print(f"Total Penyewaan: {len(all_rentals)}")
    print("=" * 60)

if __name__ == "__main__":
    test_full_workflow()
