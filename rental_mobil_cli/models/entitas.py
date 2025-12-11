from abc import ABC, abstractmethod
from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional
from utils.validators import Validator

@dataclass
class Entity(ABC):
    """Abstract Base Class untuk semua entities (Open/Closed Principle)"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @abstractmethod
    def validate(self):
        """Validasi data entity"""
        pass

class Mobil(Entity):
    """Entity untuk Mobil"""
    
    def __init__(self, merk: str, model: str, tahun: int, plat_nomor: str, 
                 harga_sewa_per_hari: float, status: str = 'tersedia', **kwargs):
        super().__init__(**kwargs)
        self.merk = merk
        self.model = model
        self.tahun = tahun
        self.plat_nomor = plat_nomor
        self.harga_sewa_per_hari = harga_sewa_per_hari
        self.status = status
    
    def validate(self):
        """Validasi data mobil"""
        Validator.validate_not_empty(self.merk, "Merk")
        Validator.validate_not_empty(self.model, "Model")
        Validator.validate_year(self.tahun)
        Validator.validate_license_plate(self.plat_nomor)
        Validator.validate_positive_number(self.harga_sewa_per_hari, "Harga sewa")
        Validator.validate_in_list(self.status, ['tersedia', 'disewa', 'perbaikan'], "Status")
    
    def __str__(self):
        return f"{self.merk} {self.model} ({self.tahun}) - {self.plat_nomor}"

class Pelanggan(Entity):
    """Entity untuk Pelanggan"""
    
    def __init__(self, nik: str, nama: str, alamat: str = '', 
                 no_telepon: str = '', email: str = '', **kwargs):
        super().__init__(**kwargs)
        self.nik = nik
        self.nama = nama
        self.alamat = alamat
        self.no_telepon = no_telepon
        self.email = email
    
    def validate(self):
        """Validasi data pelanggan"""
        Validator.validate_nik(self.nik)
        Validator.validate_not_empty(self.nama, "Nama")
        if self.email:
            Validator.validate_email(self.email)
        if self.no_telepon:
            Validator.validate_phone(self.no_telepon)
    
    def __str__(self):
        return f"{self.nama} ({self.nik})"

class Penyewaan(Entity):
    """Entity untuk Penyewaan"""
    
    def __init__(self, mobil_id: int, pelanggan_id: int, tanggal_sewa: date,
                 tanggal_kembali: date, total_hari: int, total_biaya: float,
                 tanggal_pengembalian: Optional[date] = None, denda: float = 0,
                 status: str = 'aktif', kode_penyewaan: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.mobil_id = mobil_id
        self.pelanggan_id = pelanggan_id
        self.tanggal_sewa = tanggal_sewa
        self.tanggal_kembali = tanggal_kembali
        self.tanggal_pengembalian = tanggal_pengembalian
        self.total_hari = total_hari
        self.total_biaya = total_biaya
        self.denda = denda
        self.status = status
        self.kode_penyewaan = kode_penyewaan
    
    def validate(self):
        """Validasi data penyewaan"""
        Validator.validate_positive_number(self.mobil_id, "ID Mobil")
        Validator.validate_positive_number(self.pelanggan_id, "ID Pelanggan")
        Validator.validate_date_not_past(self.tanggal_sewa)
        
        if self.tanggal_kembali <= self.tanggal_sewa:
            raise ValueError("Tanggal kembali harus setelah tanggal sewa")
        
        Validator.validate_positive_number(self.total_hari, "Total hari")
        Validator.validate_positive_number(self.total_biaya, "Total biaya")
        Validator.validate_in_list(self.status, ['aktif', 'selesai', 'terlambat'], "Status")
    
    def hitung_denda(self, harga_per_hari: float, hari_keterlambatan: int) -> float:
        """Hitung denda berdasarkan keterlambatan"""
        if hari_keterlambatan > 0:
            return harga_per_hari * hari_keterlambatan * 1.5  # Denda 150% per hari
        return 0

class Pembayaran(Entity):
    """Entity untuk Pembayaran"""
    
    def __init__(self, penyewaan_id: int, jumlah: float, 
                 metode_pembayaran: str, status: str = 'pending',
                 bukti_pembayaran: str = '', **kwargs):
        super().__init__(**kwargs)
        self.penyewaan_id = penyewaan_id
        self.jumlah = jumlah
        self.metode_pembayaran = metode_pembayaran
        self.status = status
        self.bukti_pembayaran = bukti_pembayaran
    
    def validate(self):
        """Validasi data pembayaran"""
        Validator.validate_positive_number(self.penyewaan_id, "ID Penyewaan")
        Validator.validate_positive_number(self.jumlah, "Jumlah pembayaran")
        Validator.validate_in_list(self.metode_pembayaran, 
                                 ['tunai', 'transfer', 'kartu_kredit'], 
                                 "Metode pembayaran")
        Validator.validate_in_list(self.status, ['pending', 'lunas', 'gagal'], "Status")