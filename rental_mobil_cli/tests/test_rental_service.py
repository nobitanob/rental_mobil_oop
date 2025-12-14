"""
Unit Test untuk RentalService dengan Mock
Menguji business logic penyewaan mobil
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, timedelta
import sys
import os

# Tambahkan path parent untuk import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.entitas import Mobil, Pelanggan, Penyewaan
from services.rental_service import RentalService


class TestRentalServiceSewaMobil(unittest.TestCase):
    """Test cases untuk method sewa_mobil"""
    
    def setUp(self):
        """Setup mock repositories"""
        # ══════════════════════════════════════════════════════════════
        # MOCK: Simulasi semua repository
        # ══════════════════════════════════════════════════════════════
        self.mock_mobil_repo = Mock()
        self.mock_pelanggan_repo = Mock()
        self.mock_penyewaan_repo = Mock()
        self.mock_pembayaran_repo = Mock()
        
        # Inject mock dependencies ke service
        self.service = RentalService(
            mobil_repo=self.mock_mobil_repo,
            pelanggan_repo=self.mock_pelanggan_repo,
            penyewaan_repo=self.mock_penyewaan_repo,
            pembayaran_repo=self.mock_pembayaran_repo
        )
        
        # Sample data untuk testing
        self.sample_mobil = Mobil(
            id=1,
            merk="Toyota",
            model="Avanza",
            tahun=2023,
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=350000.0,
            status="tersedia"
        )
        
        self.sample_pelanggan = Pelanggan(
            id=1,
            nik="1234567890123456",
            nama="John Doe"
        )
    
    def test_sewa_mobil_success(self):
        """Test penyewaan mobil berhasil"""
        # Arrange: Setup mock return values
        self.mock_mobil_repo.find_by_id.return_value = self.sample_mobil
        self.mock_pelanggan_repo.find_by_id.return_value = self.sample_pelanggan
        self.mock_penyewaan_repo.find_all.return_value = []  # No existing rentals
        self.mock_penyewaan_repo.create.return_value = 1  # Return new rental ID
        self.mock_mobil_repo.update_status.return_value = True
        
        # Act: Panggil method sewa_mobil
        success, message, rental_id = self.service.sewa_mobil(
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today(),
            jumlah_hari=3
        )
        
        # Assert: Verifikasi hasil
        self.assertTrue(success)
        self.assertIn("berhasil", message.lower())
        self.assertIsNotNone(rental_id)
        
        # Verifikasi mock dipanggil dengan benar
        self.mock_mobil_repo.find_by_id.assert_called_once_with(1)
        self.mock_pelanggan_repo.find_by_id.assert_called_once_with(1)
        self.mock_penyewaan_repo.create.assert_called_once()
        self.mock_mobil_repo.update_status.assert_called_once_with(1, 'disewa')
    
    def test_sewa_mobil_mobil_not_found(self):
        """Test penyewaan gagal - mobil tidak ditemukan"""
        # Arrange
        self.mock_mobil_repo.find_by_id.return_value = None
        
        # Act
        success, message, rental_id = self.service.sewa_mobil(
            mobil_id=999,
            pelanggan_id=1,
            tanggal_sewa=date.today(),
            jumlah_hari=3
        )
        
        # Assert
        self.assertFalse(success)
        self.assertIn("tidak ditemukan", message.lower())
        self.assertIsNone(rental_id)
    
    def test_sewa_mobil_mobil_not_available(self):
        """Test penyewaan gagal - mobil sedang disewa"""
        # Arrange
        mobil_disewa = Mobil(
            id=1,
            merk="Toyota",
            model="Avanza",
            tahun=2023,
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=350000.0,
            status="disewa"  # Status tidak tersedia
        )
        self.mock_mobil_repo.find_by_id.return_value = mobil_disewa
        
        # Act
        success, message, rental_id = self.service.sewa_mobil(
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today(),
            jumlah_hari=3
        )
        
        # Assert
        self.assertFalse(success)
        self.assertIn("disewa", message.lower())
    
    def test_sewa_mobil_pelanggan_not_found(self):
        """Test penyewaan gagal - pelanggan tidak ditemukan"""
        # Arrange
        self.mock_mobil_repo.find_by_id.return_value = self.sample_mobil
        self.mock_pelanggan_repo.find_by_id.return_value = None
        
        # Act
        success, message, rental_id = self.service.sewa_mobil(
            mobil_id=1,
            pelanggan_id=999,
            tanggal_sewa=date.today(),
            jumlah_hari=3
        )
        
        # Assert
        self.assertFalse(success)
        self.assertIn("pelanggan", message.lower())
    
    def test_sewa_mobil_invalid_days(self):
        """Test penyewaan gagal - jumlah hari tidak valid"""
        # Act
        success, message, rental_id = self.service.sewa_mobil(
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today(),
            jumlah_hari=0  # Invalid
        )
        
        # Assert
        self.assertFalse(success)
    
    def test_sewa_mobil_past_date(self):
        """Test penyewaan gagal - tanggal di masa lalu"""
        # Act
        past_date = date.today() - timedelta(days=1)
        success, message, rental_id = self.service.sewa_mobil(
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=past_date,
            jumlah_hari=3
        )
        
        # Assert
        self.assertFalse(success)
    
    def test_sewa_mobil_calculate_total_biaya(self):
        """Test perhitungan total biaya benar"""
        # Arrange
        harga_per_hari = 350000.0
        jumlah_hari = 5
        expected_total = harga_per_hari * jumlah_hari  # 1,750,000
        
        self.mock_mobil_repo.find_by_id.return_value = self.sample_mobil
        self.mock_pelanggan_repo.find_by_id.return_value = self.sample_pelanggan
        self.mock_penyewaan_repo.find_all.return_value = []
        self.mock_penyewaan_repo.create.return_value = 1
        
        # Act
        success, message, _ = self.service.sewa_mobil(
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today(),
            jumlah_hari=jumlah_hari
        )
        
        # Assert
        self.assertTrue(success)
        self.assertIn(f"{expected_total:,.2f}", message)


class TestRentalServicePengembalian(unittest.TestCase):
    """Test cases untuk method pengembalian_mobil"""
    
    def setUp(self):
        """Setup mock repositories"""
        self.mock_mobil_repo = Mock()
        self.mock_pelanggan_repo = Mock()
        self.mock_penyewaan_repo = Mock()
        self.mock_pembayaran_repo = Mock()
        
        self.service = RentalService(
            mobil_repo=self.mock_mobil_repo,
            pelanggan_repo=self.mock_pelanggan_repo,
            penyewaan_repo=self.mock_penyewaan_repo,
            pembayaran_repo=self.mock_pembayaran_repo
        )
        
        # Sample penyewaan aktif
        self.sample_penyewaan = Penyewaan(
            id=1,
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today() - timedelta(days=3),
            tanggal_kembali=date.today(),
            total_hari=3,
            total_biaya=1050000.0,
            status="aktif",
            kode_penyewaan="RENT-202512-0001"
        )
        
        self.sample_mobil = Mobil(
            id=1,
            merk="Toyota",
            model="Avanza",
            tahun=2023,
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=350000.0,
            status="disewa"
        )
    
    def test_pengembalian_tepat_waktu(self):
        """Test pengembalian tepat waktu - tanpa denda"""
        # Arrange
        self.mock_penyewaan_repo.find_by_id.return_value = self.sample_penyewaan
        self.mock_mobil_repo.find_by_id.return_value = self.sample_mobil
        self.mock_penyewaan_repo.update.return_value = True
        self.mock_mobil_repo.update_status.return_value = True
        
        # Act
        success, message, denda = self.service.pengembalian_mobil(
            penyewaan_id=1,
            tanggal_pengembalian=date.today()  # Tepat waktu
        )
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(denda, 0)
        self.mock_mobil_repo.update_status.assert_called_with(1, 'tersedia')
    
    def test_pengembalian_terlambat(self):
        """Test pengembalian terlambat - ada denda"""
        # Arrange
        penyewaan_terlambat = Penyewaan(
            id=1,
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today() - timedelta(days=5),
            tanggal_kembali=date.today() - timedelta(days=2),  # Harusnya 2 hari lalu
            total_hari=3,
            total_biaya=1050000.0,
            status="aktif"
        )
        
        self.mock_penyewaan_repo.find_by_id.return_value = penyewaan_terlambat
        self.mock_mobil_repo.find_by_id.return_value = self.sample_mobil
        self.mock_penyewaan_repo.update.return_value = True
        self.mock_mobil_repo.update_status.return_value = True
        
        # Act
        success, message, denda = self.service.pengembalian_mobil(
            penyewaan_id=1,
            tanggal_pengembalian=date.today()  # Terlambat 2 hari
        )
        
        # Assert
        self.assertTrue(success)
        self.assertGreater(denda, 0)  # Ada denda
        self.assertIn("denda", message.lower())
    
    def test_pengembalian_penyewaan_not_found(self):
        """Test pengembalian gagal - penyewaan tidak ditemukan"""
        # Arrange
        self.mock_penyewaan_repo.find_by_id.return_value = None
        
        # Act
        success, message, denda = self.service.pengembalian_mobil(
            penyewaan_id=999,
            tanggal_pengembalian=date.today()
        )
        
        # Assert
        self.assertFalse(success)
        self.assertIn("tidak ditemukan", message.lower())
    
    def test_pengembalian_already_returned(self):
        """Test pengembalian gagal - sudah dikembalikan"""
        # Arrange
        penyewaan_selesai = Penyewaan(
            id=1,
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today() - timedelta(days=5),
            tanggal_kembali=date.today() - timedelta(days=2),
            total_hari=3,
            total_biaya=1050000.0,
            status="selesai"  # Sudah selesai
        )
        self.mock_penyewaan_repo.find_by_id.return_value = penyewaan_selesai
        
        # Act
        success, message, denda = self.service.pengembalian_mobil(
            penyewaan_id=1,
            tanggal_pengembalian=date.today()
        )
        
        # Assert
        self.assertFalse(success)
        self.assertIn("selesai", message.lower())


class TestRentalServiceGenerateCode(unittest.TestCase):
    """Test cases untuk method _generate_rental_code"""
    
    def setUp(self):
        """Setup"""
        self.mock_mobil_repo = Mock()
        self.mock_pelanggan_repo = Mock()
        self.mock_penyewaan_repo = Mock()
        self.mock_pembayaran_repo = Mock()
        
        self.service = RentalService(
            mobil_repo=self.mock_mobil_repo,
            pelanggan_repo=self.mock_pelanggan_repo,
            penyewaan_repo=self.mock_penyewaan_repo,
            pembayaran_repo=self.mock_pembayaran_repo
        )
    
    def test_generate_first_code(self):
        """Test generate kode pertama"""
        # Arrange
        self.mock_penyewaan_repo.find_all.return_value = []
        
        # Act
        code = self.service._generate_rental_code()
        
        # Assert
        self.assertTrue(code.startswith("RENT-"))
        self.assertIn("-0001", code)
    
    def test_generate_next_code(self):
        """Test generate kode berikutnya"""
        # Arrange
        existing_penyewaan = Penyewaan(
            id=1,
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today(),
            tanggal_kembali=date.today(),
            total_hari=3,
            total_biaya=1050000.0,
            kode_penyewaan="RENT-202512-0005"
        )
        self.mock_penyewaan_repo.find_all.return_value = [existing_penyewaan]
        
        # Act
        code = self.service._generate_rental_code()
        
        # Assert
        self.assertIn("-0006", code)  # Increment dari 0005


class TestRentalServiceIntegration(unittest.TestCase):
    """Integration test untuk skenario lengkap"""
    
    def setUp(self):
        """Setup mock repositories"""
        self.mock_mobil_repo = Mock()
        self.mock_pelanggan_repo = Mock()
        self.mock_penyewaan_repo = Mock()
        self.mock_pembayaran_repo = Mock()
        
        self.service = RentalService(
            mobil_repo=self.mock_mobil_repo,
            pelanggan_repo=self.mock_pelanggan_repo,
            penyewaan_repo=self.mock_penyewaan_repo,
            pembayaran_repo=self.mock_pembayaran_repo
        )
    
    def test_full_rental_cycle(self):
        """Test siklus lengkap: sewa -> kembalikan"""
        # ══════════════════════════════════════════════════════════════
        # STEP 1: PENYEWAAN
        # ══════════════════════════════════════════════════════════════
        mobil = Mobil(
            id=1, merk="Toyota", model="Avanza", tahun=2023,
            plat_nomor="B 1234 ABC", harga_sewa_per_hari=350000.0, status="tersedia"
        )
        pelanggan = Pelanggan(id=1, nik="1234567890123456", nama="John Doe")
        
        self.mock_mobil_repo.find_by_id.return_value = mobil
        self.mock_pelanggan_repo.find_by_id.return_value = pelanggan
        self.mock_penyewaan_repo.find_all.return_value = []
        self.mock_penyewaan_repo.create.return_value = 1
        
        # Sewa mobil
        success, message, rental_id = self.service.sewa_mobil(
            mobil_id=1, pelanggan_id=1, tanggal_sewa=date.today(), jumlah_hari=3
        )
        
        self.assertTrue(success, "Penyewaan harus berhasil")
        self.assertEqual(rental_id, 1)
        
        # ══════════════════════════════════════════════════════════════
        # STEP 2: PENGEMBALIAN
        # ══════════════════════════════════════════════════════════════
        penyewaan = Penyewaan(
            id=1, mobil_id=1, pelanggan_id=1,
            tanggal_sewa=date.today(), tanggal_kembali=date.today() + timedelta(days=3),
            total_hari=3, total_biaya=1050000.0, status="aktif"
        )
        
        self.mock_penyewaan_repo.find_by_id.return_value = penyewaan
        self.mock_penyewaan_repo.update.return_value = True
        
        # Kembalikan mobil (tepat waktu)
        success, message, denda = self.service.pengembalian_mobil(
            penyewaan_id=1, tanggal_pengembalian=date.today() + timedelta(days=3)
        )
        
        self.assertTrue(success, "Pengembalian harus berhasil")
        self.assertEqual(denda, 0, "Tidak ada denda untuk pengembalian tepat waktu")


if __name__ == '__main__':
    unittest.main(verbosity=2)
