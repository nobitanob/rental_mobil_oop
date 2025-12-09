#!/usr/bin/env python3
"""Test rental creation with debug output"""

from datetime import date
from database.connection import DatabaseManager
from models.repositories import MobilRepository, PelangganRepository, PenyewaanRepository, PembayaranRepository
from services.rental_service import RentalService

def test_rental_creation():
    """Test creating a rental"""
    # Initialize database
    db_manager = DatabaseManager()
    
    # Create repositories
    mobil_repo = MobilRepository(db_manager)
    pelanggan_repo = PelangganRepository(db_manager)
    penyewaan_repo = PenyewaanRepository(db_manager)
    pembayaran_repo = PembayaranRepository(db_manager)
    
    # Create service
    service = RentalService(
        mobil_repo=mobil_repo,
        pelanggan_repo=pelanggan_repo,
        penyewaan_repo=penyewaan_repo,
        pembayaran_repo=pembayaran_repo
    )
    
    # Test data
    mobil_id = 8
    pelanggan_id = 8
    tanggal_sewa = date.today()
    jumlah_hari = 3
    
    print(f"Testing rental creation:")
    print(f"  ID Mobil: {mobil_id}")
    print(f"  ID Pelanggan: {pelanggan_id}")
    print(f"  Tanggal Sewa: {tanggal_sewa}")
    print(f"  Jumlah Hari: {jumlah_hari}")
    print()
    
    # Debug: Check existing codes before creating
    print("Before creation:")
    all_rentals = penyewaan_repo.find_all()
    print(f"  Total rentals: {len(all_rentals)}")
    for r in all_rentals:
        print(f"    Code: {r.kode_penyewaan}")
    
    try:
        # Manually call the generate function to debug
        code = service._generate_rental_code()
        print(f"\nGenerated code: {code}")
        
        # Now try the actual sewa_mobil
        success, message, rental_id = service.sewa_mobil(mobil_id, pelanggan_id, tanggal_sewa, jumlah_hari)
        
        if success:
            print(f"\n✓ Rental created successfully!")
            print(f"  Message: {message}")
        else:
            print(f"\n✗ Error: {message}")
    except Exception as e:
        print(f"\n✗ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rental_creation()
