"""
Unit Test untuk Repository Classes dengan Mock
Menguji MobilRepository, PelangganRepository, PenyewaanRepository
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime
import sys
import os

# Tambahkan path parent untuk import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.entitas import Mobil, Pelanggan, Penyewaan
from models.repositories import MobilRepository, PelangganRepository, PenyewaanRepository


class TestMobilRepository(unittest.TestCase):
    """Test cases untuk MobilRepository dengan Mock Database"""
    
    def setUp(self):
        """Setup mock database manager"""
        # ══════════════════════════════════════════════════════════════
        # MOCK: Simulasi DatabaseManager tanpa koneksi database nyata
        # ══════════════════════════════════════════════════════════════
        self.mock_db_manager = Mock()
        self.repo = MobilRepository(self.mock_db_manager)
        
        # Data mobil untuk testing
        self.sample_mobil_data = {
            'id': 1,
            'merk': 'Toyota',
            'model': 'Avanza',
            'tahun': 2023,
            'plat_nomor': 'B 1234 ABC',
            'harga_sewa_per_hari': 350000.0,
            'status': 'tersedia',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def test_find_by_id_found(self):
        """Test find_by_id ketika mobil ditemukan"""
        # Arrange: Setup mock return value
        self.mock_db_manager.execute_query.return_value = [self.sample_mobil_data]
        
        # Act: Panggil method
        result = self.repo.find_by_id(1)
        
        # Assert: Verifikasi hasil
        self.assertIsNotNone(result)
        self.assertEqual(result.merk, "Toyota")
        self.assertEqual(result.model, "Avanza")
        self.mock_db_manager.execute_query.assert_called_once()
    
    def test_find_by_id_not_found(self):
        """Test find_by_id ketika mobil tidak ditemukan"""
        # Arrange: Mock return empty list
        self.mock_db_manager.execute_query.return_value = []
        
        # Act
        result = self.repo.find_by_id(999)
        
        # Assert
        self.assertIsNone(result)
    
    def test_find_all_with_data(self):
        """Test find_all dengan data"""
        # Arrange: Mock multiple data
        self.mock_db_manager.execute_query.return_value = [
            self.sample_mobil_data,
            {
                'id': 2,
                'merk': 'Honda',
                'model': 'Jazz',
                'tahun': 2022,
                'plat_nomor': 'D 5678 XYZ',
                'harga_sewa_per_hari': 300000.0,
                'status': 'tersedia',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        
        # Act
        results = self.repo.find_all()
        
        # Assert
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].merk, "Toyota")
        self.assertEqual(results[1].merk, "Honda")
    
    def test_find_all_empty(self):
        """Test find_all ketika tidak ada data"""
        # Arrange
        self.mock_db_manager.execute_query.return_value = []
        
        # Act
        results = self.repo.find_all()
        
        # Assert
        self.assertEqual(len(results), 0)
    
    def test_find_all_by_status(self):
        """Test find_all dengan filter status"""
        # Arrange
        self.mock_db_manager.execute_query.return_value = [self.sample_mobil_data]
        
        # Act
        results = self.repo.find_all(status='tersedia')
        
        # Assert
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, "tersedia")
        # Verifikasi query dipanggil
        self.mock_db_manager.execute_query.assert_called_once()
    
    def test_create_success(self):
        """Test create mobil berhasil"""
        # Arrange
        mobil = Mobil(
            merk="Toyota",
            model="Avanza",
            tahun=2023,
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=350000.0
        )
        self.mock_db_manager.execute_query.return_value = 1  # Return new ID
        
        # Act
        result_id = self.repo.create(mobil)
        
        # Assert
        self.assertEqual(result_id, 1)
        self.mock_db_manager.execute_query.assert_called_once()
    
    def test_update_success(self):
        """Test update mobil berhasil"""
        # Arrange
        mobil = Mobil(
            id=1,
            merk="Toyota",
            model="Avanza Veloz",  # Updated model
            tahun=2023,
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=400000.0  # Updated price
        )
        self.mock_db_manager.execute_query.return_value = True
        
        # Act
        result = self.repo.update(mobil)
        
        # Assert
        self.assertTrue(result)
    
    def test_delete_success(self):
        """Test delete mobil berhasil"""
        # Arrange
        self.mock_db_manager.execute_query.return_value = True
        
        # Act
        result = self.repo.delete(1)
        
        # Assert
        self.assertTrue(result)


class TestPelangganRepository(unittest.TestCase):
    """Test cases untuk PelangganRepository dengan Mock"""
    
    def setUp(self):
        """Setup mock database manager"""
        self.mock_db_manager = Mock()
        self.repo = PelangganRepository(self.mock_db_manager)
        
        self.sample_pelanggan_data = {
            'id': 1,
            'nik': '1234567890123456',
            'nama': 'John Doe',
            'alamat': 'Jl. Test No. 123',
            'no_telepon': '081234567890',
            'email': 'john@example.com',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def test_find_by_id_found(self):
        """Test find_by_id pelanggan ditemukan"""
        # Arrange
        self.mock_db_manager.execute_query.return_value = [self.sample_pelanggan_data]
        
        # Act
        result = self.repo.find_by_id(1)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.nama, "John Doe")
        self.assertEqual(result.nik, "1234567890123456")
    
    def test_find_by_nik_found(self):
        """Test find_by_nik pelanggan ditemukan"""
        # Arrange
        self.mock_db_manager.execute_query.return_value = [self.sample_pelanggan_data]
        
        # Act
        result = self.repo.find_by_nik("1234567890123456")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.nama, "John Doe")
    
    def test_create_success(self):
        """Test create pelanggan berhasil"""
        # Arrange
        pelanggan = Pelanggan(
            nik="1234567890123456",
            nama="John Doe",
            alamat="Jl. Test",
            no_telepon="081234567890",
            email="john@example.com"
        )
        self.mock_db_manager.execute_query.return_value = 1
        
        # Act
        result_id = self.repo.create(pelanggan)
        
        # Assert
        self.assertEqual(result_id, 1)


class TestPenyewaanRepository(unittest.TestCase):
    """Test cases untuk PenyewaanRepository dengan Mock"""
    
    def setUp(self):
        """Setup mock database manager"""
        self.mock_db_manager = Mock()
        self.repo = PenyewaanRepository(self.mock_db_manager)
        
        self.sample_penyewaan_data = {
            'id': 1,
            'mobil_id': 1,
            'pelanggan_id': 1,
            'kode_penyewaan': 'RENT-202512-0001',
            'tanggal_sewa': date.today(),
            'tanggal_kembali': date.today(),
            'tanggal_pengembalian': None,
            'total_hari': 3,
            'total_biaya': 1050000.0,
            'denda': 0,
            'status': 'aktif',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    def test_find_by_id_found(self):
        """Test find_by_id penyewaan ditemukan"""
        # Arrange
        self.mock_db_manager.execute_query.return_value = [self.sample_penyewaan_data]
        
        # Act
        result = self.repo.find_by_id(1)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.kode_penyewaan, "RENT-202512-0001")
        self.assertEqual(result.status, "aktif")
    
    def test_find_by_status_aktif(self):
        """Test find_all dengan status aktif"""
        # Arrange
        self.mock_db_manager.execute_query.return_value = [self.sample_penyewaan_data]
        
        # Act
        results = self.repo.find_all()
        aktif_results = [r for r in results if r.status == 'aktif']
        
        # Assert
        self.assertEqual(len(aktif_results), 1)
        self.assertEqual(aktif_results[0].status, "aktif")
    
    def test_create_success(self):
        """Test create penyewaan berhasil"""
        # Arrange: tanggal_kembali harus setelah tanggal_sewa
        from datetime import timedelta
        penyewaan = Penyewaan(
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today(),
            tanggal_kembali=date.today() + timedelta(days=3),  # 3 hari kemudian
            total_hari=3,
            total_biaya=1050000.0,
            kode_penyewaan="RENT-202512-0001"
        )
        self.mock_db_manager.execute_query.return_value = 1
        
        # Act
        result_id = self.repo.create(penyewaan)
        
        # Assert
        self.assertEqual(result_id, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
