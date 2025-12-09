#!/usr/bin/env python3
"""Test creating another rental to verify sequence counter"""

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
    
    # Test data - different vehicle/customer
    mobil_id = 5  
    pelanggan_id = 3
    tanggal_sewa = date.today()
    jumlah_hari = 2
    
    print(f"Testing another rental creation:")
    print(f"  ID Mobil: {mobil_id}")
    print(f"  ID Pelanggan: {pelanggan_id}")
    print(f"  Jumlah Hari: {jumlah_hari}")
    print()
    
    try:
        success, message, rental_id = service.sewa_mobil(mobil_id, pelanggan_id, tanggal_sewa, jumlah_hari)
        
        if success:
            print(f"✓ Rental created successfully!")
            print(f"  Message: {message}")
            print(f"  Rental ID: {rental_id}")
        else:
            print(f"✗ Error: {message}")
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rental_creation()
