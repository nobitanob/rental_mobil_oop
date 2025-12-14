"""
Unit Test untuk Entity Classes
Menguji class Mobil, Pelanggan, Penyewaan, Pembayaran
"""
import unittest
from datetime import date, datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Tambahkan path parent untuk import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.entitas import Mobil, Pelanggan, Penyewaan, Pembayaran


class TestMobilEntity(unittest.TestCase):
    """Test cases untuk Entity Mobil"""
    
    def setUp(self):
        """Setup data test sebelum setiap test case"""
        self.mobil_valid = Mobil(
            merk="Toyota",
            model="Avanza",
            tahun=2023,
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=350000.0,
            status="tersedia"
        )
    
    def test_mobil_creation_success(self):
        """Test pembuatan objek Mobil berhasil"""
        self.assertEqual(self.mobil_valid.merk, "Toyota")
        self.assertEqual(self.mobil_valid.model, "Avanza")
        self.assertEqual(self.mobil_valid.tahun, 2023)
        self.assertEqual(self.mobil_valid.plat_nomor, "B 1234 ABC")
        self.assertEqual(self.mobil_valid.harga_sewa_per_hari, 350000.0)
        self.assertEqual(self.mobil_valid.status, "tersedia")
    
    def test_mobil_str_representation(self):
        """Test representasi string Mobil"""
        expected = "Toyota Avanza (2023) - B 1234 ABC"
        self.assertEqual(str(self.mobil_valid), expected)
    
    def test_mobil_validate_success(self):
        """Test validasi Mobil berhasil"""
        # Tidak boleh raise exception
        try:
            self.mobil_valid.validate()
            validation_passed = True
        except ValueError:
            validation_passed = False
        self.assertTrue(validation_passed)
    
    def test_mobil_validate_empty_merk(self):
        """Test validasi gagal jika merk kosong"""
        mobil = Mobil(
            merk="",
            model="Avanza",
            tahun=2023,
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=350000.0
        )
        with self.assertRaises(ValueError) as context:
            mobil.validate()
        self.assertIn("Merk", str(context.exception))
    
    def test_mobil_validate_invalid_plat(self):
        """Test validasi gagal jika plat nomor invalid"""
        mobil = Mobil(
            merk="Toyota",
            model="Avanza",
            tahun=2023,
            plat_nomor="INVALID",
            harga_sewa_per_hari=350000.0
        )
        with self.assertRaises(ValueError) as context:
            mobil.validate()
        self.assertIn("plat", str(context.exception).lower())
    
    def test_mobil_validate_invalid_year(self):
        """Test validasi gagal jika tahun invalid"""
        mobil = Mobil(
            merk="Toyota",
            model="Avanza",
            tahun=1800,  # Terlalu lama
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=350000.0
        )
        with self.assertRaises(ValueError) as context:
            mobil.validate()
        self.assertIn("Tahun", str(context.exception))
    
    def test_mobil_validate_negative_price(self):
        """Test validasi gagal jika harga negatif"""
        mobil = Mobil(
            merk="Toyota",
            model="Avanza",
            tahun=2023,
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=-100000.0  # Negatif
        )
        with self.assertRaises(ValueError) as context:
            mobil.validate()
        self.assertIn("Harga", str(context.exception))


class TestPelangganEntity(unittest.TestCase):
    """Test cases untuk Entity Pelanggan"""
    
    def setUp(self):
        """Setup data test"""
        self.pelanggan_valid = Pelanggan(
            nik="1234567890123456",
            nama="John Doe",
            alamat="Jl. Test No. 123",
            no_telepon="081234567890",
            email="john@example.com"
        )
    
    def test_pelanggan_creation_success(self):
        """Test pembuatan objek Pelanggan berhasil"""
        self.assertEqual(self.pelanggan_valid.nik, "1234567890123456")
        self.assertEqual(self.pelanggan_valid.nama, "John Doe")
        self.assertEqual(self.pelanggan_valid.email, "john@example.com")
    
    def test_pelanggan_str_representation(self):
        """Test representasi string Pelanggan"""
        expected = "John Doe (1234567890123456)"
        self.assertEqual(str(self.pelanggan_valid), expected)
    
    def test_pelanggan_validate_success(self):
        """Test validasi Pelanggan berhasil"""
        try:
            self.pelanggan_valid.validate()
            validation_passed = True
        except ValueError:
            validation_passed = False
        self.assertTrue(validation_passed)
    
    def test_pelanggan_validate_invalid_nik(self):
        """Test validasi gagal jika NIK invalid"""
        pelanggan = Pelanggan(
            nik="12345",  # Kurang dari 16 digit
            nama="John Doe"
        )
        with self.assertRaises(ValueError) as context:
            pelanggan.validate()
        self.assertIn("NIK", str(context.exception))
    
    def test_pelanggan_validate_empty_nama(self):
        """Test validasi gagal jika nama kosong"""
        pelanggan = Pelanggan(
            nik="1234567890123456",
            nama=""
        )
        with self.assertRaises(ValueError) as context:
            pelanggan.validate()
        self.assertIn("Nama", str(context.exception))
    
    def test_pelanggan_validate_invalid_email(self):
        """Test validasi gagal jika email invalid"""
        pelanggan = Pelanggan(
            nik="1234567890123456",
            nama="John Doe",
            email="invalid-email"
        )
        with self.assertRaises(ValueError) as context:
            pelanggan.validate()
        self.assertIn("email", str(context.exception).lower())


class TestPenyewaanEntity(unittest.TestCase):
    """Test cases untuk Entity Penyewaan"""
    
    def setUp(self):
        """Setup data test"""
        self.penyewaan_valid = Penyewaan(
            mobil_id=1,
            pelanggan_id=1,
            tanggal_sewa=date.today(),
            tanggal_kembali=date.today(),
            total_hari=3,
            total_biaya=1050000.0,
            status="aktif",
            kode_penyewaan="RENT-202512-0001"
        )
    
    def test_penyewaan_creation_success(self):
        """Test pembuatan objek Penyewaan berhasil"""
        self.assertEqual(self.penyewaan_valid.mobil_id, 1)
        self.assertEqual(self.penyewaan_valid.pelanggan_id, 1)
        self.assertEqual(self.penyewaan_valid.total_hari, 3)
        self.assertEqual(self.penyewaan_valid.status, "aktif")
    
    def test_penyewaan_hitung_denda(self):
        """Test perhitungan denda keterlambatan"""
        harga_per_hari = 350000.0
        hari_keterlambatan = 2
        
        # Denda biasanya 1.5x atau 2x harga per hari
        denda = self.penyewaan_valid.hitung_denda(harga_per_hari, hari_keterlambatan)
        
        # Asumsi denda = harga_per_hari * hari_keterlambatan * 1.5
        expected_denda = harga_per_hari * hari_keterlambatan * 1.5
        self.assertEqual(denda, expected_denda)


class TestPembayaranEntity(unittest.TestCase):
    """Test cases untuk Entity Pembayaran"""
    
    def setUp(self):
        """Setup data test"""
        self.pembayaran_valid = Pembayaran(
            penyewaan_id=1,
            jumlah=1050000.0,
            metode_pembayaran="transfer",
            status="lunas"
        )
    
    def test_pembayaran_creation_success(self):
        """Test pembuatan objek Pembayaran berhasil"""
        self.assertEqual(self.pembayaran_valid.penyewaan_id, 1)
        self.assertEqual(self.pembayaran_valid.jumlah, 1050000.0)
        self.assertEqual(self.pembayaran_valid.metode_pembayaran, "transfer")
        self.assertEqual(self.pembayaran_valid.status, "lunas")


if __name__ == '__main__':
    unittest.main(verbosity=2)
