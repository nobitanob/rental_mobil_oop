"""
Unit Test untuk Validator Class
Menguji semua method validasi
"""
import unittest
from datetime import date, timedelta
import sys
import os

# Tambahkan path parent untuk import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import Validator


class TestValidatorNotEmpty(unittest.TestCase):
    """Test cases untuk validate_not_empty"""
    
    def test_valid_string(self):
        """Test string valid tidak raise exception"""
        try:
            Validator.validate_not_empty("Hello", "Field")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_empty_string(self):
        """Test string kosong raise ValueError"""
        with self.assertRaises(ValueError) as context:
            Validator.validate_not_empty("", "Nama")
        self.assertIn("Nama", str(context.exception))
    
    def test_whitespace_only(self):
        """Test string hanya whitespace raise ValueError"""
        with self.assertRaises(ValueError):
            Validator.validate_not_empty("   ", "Field")
    
    def test_none_value(self):
        """Test None value raise ValueError"""
        with self.assertRaises(ValueError):
            Validator.validate_not_empty(None, "Field")


class TestValidatorPositiveNumber(unittest.TestCase):
    """Test cases untuk validate_positive_number"""
    
    def test_positive_integer(self):
        """Test angka positif integer"""
        try:
            Validator.validate_positive_number(10, "Jumlah")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_positive_float(self):
        """Test angka positif float"""
        try:
            Validator.validate_positive_number(10.5, "Harga")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_zero(self):
        """Test angka nol raise ValueError"""
        with self.assertRaises(ValueError) as context:
            Validator.validate_positive_number(0, "Jumlah")
        self.assertIn("Jumlah", str(context.exception))
    
    def test_negative(self):
        """Test angka negatif raise ValueError"""
        with self.assertRaises(ValueError):
            Validator.validate_positive_number(-5, "Harga")


class TestValidatorYear(unittest.TestCase):
    """Test cases untuk validate_year"""
    
    def test_valid_year(self):
        """Test tahun valid"""
        try:
            Validator.validate_year(2023)
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_year_1900(self):
        """Test tahun 1900 valid"""
        try:
            Validator.validate_year(1900)
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_year_too_old(self):
        """Test tahun terlalu lama raise ValueError"""
        with self.assertRaises(ValueError) as context:
            Validator.validate_year(1800)
        self.assertIn("Tahun", str(context.exception))
    
    def test_year_future(self):
        """Test tahun terlalu jauh di masa depan raise ValueError"""
        with self.assertRaises(ValueError):
            Validator.validate_year(2100)


class TestValidatorLicensePlate(unittest.TestCase):
    """Test cases untuk validate_license_plate"""
    
    def test_valid_plate_format1(self):
        """Test plat nomor format valid: B 1234 ABC"""
        try:
            Validator.validate_license_plate("B 1234 ABC")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_valid_plate_format2(self):
        """Test plat nomor format valid: D 5678 XY"""
        try:
            Validator.validate_license_plate("D 5678 XY")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_invalid_plate_no_space(self):
        """Test plat nomor tanpa spasi"""
        with self.assertRaises(ValueError):
            Validator.validate_license_plate("B1234ABC")
    
    def test_invalid_plate_format(self):
        """Test plat nomor format salah"""
        with self.assertRaises(ValueError):
            Validator.validate_license_plate("INVALID")


class TestValidatorNIK(unittest.TestCase):
    """Test cases untuk validate_nik"""
    
    def test_valid_nik(self):
        """Test NIK 16 digit valid"""
        try:
            Validator.validate_nik("1234567890123456")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_nik_too_short(self):
        """Test NIK kurang dari 16 digit"""
        with self.assertRaises(ValueError) as context:
            Validator.validate_nik("12345")
        self.assertIn("NIK", str(context.exception))
    
    def test_nik_too_long(self):
        """Test NIK lebih dari 16 digit"""
        with self.assertRaises(ValueError):
            Validator.validate_nik("12345678901234567890")
    
    def test_nik_with_letters(self):
        """Test NIK mengandung huruf"""
        with self.assertRaises(ValueError):
            Validator.validate_nik("123456789012345A")


class TestValidatorEmail(unittest.TestCase):
    """Test cases untuk validate_email"""
    
    def test_valid_email(self):
        """Test email format valid"""
        try:
            Validator.validate_email("john@example.com")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_valid_email_with_subdomain(self):
        """Test email dengan subdomain"""
        try:
            Validator.validate_email("user@mail.example.com")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_invalid_email_no_at(self):
        """Test email tanpa @"""
        with self.assertRaises(ValueError):
            Validator.validate_email("johnexample.com")
    
    def test_invalid_email_no_domain(self):
        """Test email tanpa domain"""
        with self.assertRaises(ValueError):
            Validator.validate_email("john@")


class TestValidatorPhone(unittest.TestCase):
    """Test cases untuk validate_phone"""
    
    def test_valid_phone(self):
        """Test nomor telepon valid"""
        try:
            Validator.validate_phone("081234567890")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_phone_not_start_with_08(self):
        """Test nomor tidak dimulai 08"""
        with self.assertRaises(ValueError):
            Validator.validate_phone("021234567890")
    
    def test_phone_too_short(self):
        """Test nomor terlalu pendek"""
        with self.assertRaises(ValueError):
            Validator.validate_phone("08123")


class TestValidatorInList(unittest.TestCase):
    """Test cases untuk validate_in_list"""
    
    def test_value_in_list(self):
        """Test value ada dalam list"""
        valid_list = ['tersedia', 'disewa', 'perbaikan']
        try:
            Validator.validate_in_list("tersedia", valid_list, "Status")
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_value_not_in_list(self):
        """Test value tidak ada dalam list"""
        valid_list = ['tersedia', 'disewa', 'perbaikan']
        with self.assertRaises(ValueError) as context:
            Validator.validate_in_list("invalid", valid_list, "Status")
        self.assertIn("Status", str(context.exception))


class TestValidatorDateNotPast(unittest.TestCase):
    """Test cases untuk validate_date_not_past"""
    
    def test_today_date(self):
        """Test tanggal hari ini valid"""
        try:
            Validator.validate_date_not_past(date.today())
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_future_date(self):
        """Test tanggal masa depan valid"""
        future_date = date.today() + timedelta(days=7)
        try:
            Validator.validate_date_not_past(future_date)
            passed = True
        except ValueError:
            passed = False
        self.assertTrue(passed)
    
    def test_past_date(self):
        """Test tanggal masa lalu raise ValueError"""
        past_date = date.today() - timedelta(days=1)
        with self.assertRaises(ValueError) as context:
            Validator.validate_date_not_past(past_date)
        self.assertIn("masa lalu", str(context.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
