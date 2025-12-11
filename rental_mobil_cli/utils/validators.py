import re
from datetime import date, datetime
from typing import List

class Validator:
    """Class utility untuk validasi (DRY Principle)"""
    
    @staticmethod
    def validate_not_empty(value: str, field_name: str):
        """Validasi field tidak boleh kosong"""
        if not value or not value.strip():
            raise ValueError(f"{field_name} tidak boleh kosong")
    
    @staticmethod
    def validate_positive_number(value: float, field_name: str):
        """Validasi angka positif"""
        if value <= 0:
            raise ValueError(f"{field_name} harus lebih dari 0")
    
    @staticmethod
    def validate_year(year: int):
        """Validasi tahun"""
        current_year = datetime.now().year
        if year < 1900 or year > current_year + 1:
            raise ValueError(f"Tahun harus antara 1900 dan {current_year + 1}")
    
    @staticmethod
    def validate_license_plate(plate: str):
        """Validasi plat nomor"""
        pattern = r'^[A-Za-z]+\s\d+\s[A-Za-z]+$'
        if not re.match(pattern, plate):
            raise ValueError("Format plat nomor tidak valid. Contoh: B 1234 ABC")
    
    @staticmethod
    def validate_nik(nik: str):
        """Validasi NIK"""
        if not nik.isdigit() or len(nik) != 16:
            raise ValueError("NIK harus 16 digit angka")
    
    @staticmethod
    def validate_email(email: str):
        """Validasi email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Format email tidak valid")
    
    @staticmethod
    def validate_phone(phone: str):
        """Validasi nomor telepon"""
        pattern = r'^08[1-9][0-9]{7,10}$'
        if not re.match(pattern, phone):
            raise ValueError("Format nomor telepon tidak valid. Harus diawali 08")
    
    @staticmethod
    def validate_in_list(value: str, valid_list: List[str], field_name: str):
        """Validasi value ada dalam list"""
        if value not in valid_list:
            raise ValueError(f"{field_name} harus salah satu dari: {', '.join(valid_list)}")
    
    @staticmethod
    def validate_date_not_past(check_date: date):
        """Validasi tanggal tidak boleh di masa lalu"""
        if check_date < date.today():
            raise ValueError("Tanggal tidak boleh di masa lalu")