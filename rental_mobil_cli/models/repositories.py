from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from database.connection import DatabaseManager
from models.entitas import Mobil, Pelanggan, Penyewaan, Pembayaran

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """Abstract Base Class untuk repositories (Interface Segregation Principle)"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    @abstractmethod
    def create(self, entity: T) -> int:
        pass
    
    @abstractmethod
    def find_by_id(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[T]:
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

class MobilRepository(Repository[Mobil]):
    """Repository untuk entity Mobil"""
    
    def create(self, mobil: Mobil) -> int:
        mobil.validate()
        query = """
        INSERT INTO mobil (merk, model, tahun, plat_nomor, harga_sewa_per_hari, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (mobil.merk, mobil.model, mobil.tahun, mobil.plat_nomor,
                 mobil.harga_sewa_per_hari, mobil.status)
        
        result = self.db_manager.execute_query(query, params, fetch=True)
        return result
    
    def find_by_id(self, id: int) -> Optional[Mobil]:
        query = "SELECT * FROM mobil WHERE id = %s"
        result = self.db_manager.execute_query(query, (id,), fetch=True)
        
        if result:
            data = result[0]
            return Mobil(
                id=data['id'],
                merk=data['merk'],
                model=data['model'],
                tahun=data['tahun'],
                plat_nomor=data['plat_nomor'],
                harga_sewa_per_hari=float(data['harga_sewa_per_hari']),
                status=data['status'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
        return None
    
    def find_all(self, status: Optional[str] = None) -> List[Mobil]:
        if status:
            query = "SELECT * FROM mobil WHERE status = %s"
            results = self.db_manager.execute_query(query, (status,), fetch=True)
        else:
            query = "SELECT * FROM mobil"
            results = self.db_manager.execute_query(query, fetch=True)
        
        mobils = []
        for data in results:
            mobil = Mobil(
                id=data['id'],
                merk=data['merk'],
                model=data['model'],
                tahun=data['tahun'],
                plat_nomor=data['plat_nomor'],
                harga_sewa_per_hari=float(data['harga_sewa_per_hari']),
                status=data['status'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            mobils.append(mobil)
        return mobils
    
    def update(self, mobil: Mobil) -> bool:
        mobil.validate()
        query = """
        UPDATE mobil 
        SET merk = %s, model = %s, tahun = %s, plat_nomor = %s, 
            harga_sewa_per_hari = %s, status = %s
        WHERE id = %s
        """
        params = (mobil.merk, mobil.model, mobil.tahun, mobil.plat_nomor,
                 mobil.harga_sewa_per_hari, mobil.status, mobil.id)
        
        rows_affected = self.db_manager.execute_query(query, params)
        return rows_affected > 0
    
    def delete(self, id: int) -> bool:
        query = "DELETE FROM mobil WHERE id = %s"
        rows_affected = self.db_manager.execute_query(query, (id,))
        return rows_affected > 0
    
    def find_available(self) -> List[Mobil]:
        """Method khusus untuk mencari mobil yang tersedia"""
        return self.find_all('tersedia')
    
    def update_status(self, mobil_id: int, status: str) -> bool:
        """Update status mobil"""
        query = "UPDATE mobil SET status = %s WHERE id = %s"
        rows_affected = self.db_manager.execute_query(query, (status, mobil_id))
        return rows_affected > 0

class PelangganRepository(Repository[Pelanggan]):
    """Repository untuk entity Pelanggan"""
    
    def create(self, pelanggan: Pelanggan) -> int:
        pelanggan.validate()
        query = """
        INSERT INTO pelanggan (nik, nama, alamat, no_telepon, email)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (pelanggan.nik, pelanggan.nama, pelanggan.alamat,
                 pelanggan.no_telepon, pelanggan.email)
        
        result = self.db_manager.execute_query(query, params, fetch=True)
        return result
    
    def find_by_id(self, id: int) -> Optional[Pelanggan]:
        query = "SELECT * FROM pelanggan WHERE id = %s"
        result = self.db_manager.execute_query(query, (id,), fetch=True)
        
        if result:
            data = result[0]
            return Pelanggan(
                id=data['id'],
                nik=data['nik'],
                nama=data['nama'],
                alamat=data['alamat'],
                no_telepon=data['no_telepon'],
                email=data['email'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
        return None
    
    def find_all(self) -> List[Pelanggan]:
        query = "SELECT * FROM pelanggan"
        results = self.db_manager.execute_query(query, fetch=True)
        
        pelanggans = []
        for data in results:
            pelanggan = Pelanggan(
                id=data['id'],
                nik=data['nik'],
                nama=data['nama'],
                alamat=data['alamat'],
                no_telepon=data['no_telepon'],
                email=data['email'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            pelanggans.append(pelanggan)
        return pelanggans
    
    def update(self, pelanggan: Pelanggan) -> bool:
        pelanggan.validate()
        query = """
        UPDATE pelanggan 
        SET nik = %s, nama = %s, alamat = %s, no_telepon = %s, email = %s
        WHERE id = %s
        """
        params = (pelanggan.nik, pelanggan.nama, pelanggan.alamat,
                 pelanggan.no_telepon, pelanggan.email, pelanggan.id)
        
        rows_affected = self.db_manager.execute_query(query, params)
        return rows_affected > 0
    
    def delete(self, id: int) -> bool:
        query = "DELETE FROM pelanggan WHERE id = %s"
        rows_affected = self.db_manager.execute_query(query, (id,))
        return rows_affected > 0
    
    def find_by_nik(self, nik: str) -> Optional[Pelanggan]:
        """Find pelanggan by NIK"""
        query = "SELECT * FROM pelanggan WHERE nik = %s"
        result = self.db_manager.execute_query(query, (nik,), fetch=True)
        
        if result:
            data = result[0]
            return Pelanggan(
                id=data['id'],
                nik=data['nik'],
                nama=data['nama'],
                alamat=data['alamat'],
                no_telepon=data['no_telepon'],
                email=data['email'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
        return None

class PenyewaanRepository(Repository[Penyewaan]):
    """Repository untuk entity Penyewaan"""
    
    def create(self, penyewaan: Penyewaan) -> int:
        penyewaan.validate()
        query = """
        INSERT INTO penyewaan 
        (kode_penyewaan, mobil_id, pelanggan_id, tanggal_sewa, tanggal_kembali, 
         tanggal_pengembalian, total_hari, total_biaya, denda, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (penyewaan.kode_penyewaan, penyewaan.mobil_id, penyewaan.pelanggan_id,
                 penyewaan.tanggal_sewa, penyewaan.tanggal_kembali,
                 penyewaan.tanggal_pengembalian, penyewaan.total_hari,
                 penyewaan.total_biaya, penyewaan.denda, penyewaan.status)
        
        result = self.db_manager.execute_query(query, params, fetch=True)
        return result
    
    def find_by_id(self, id: int) -> Optional[Penyewaan]:
        query = "SELECT * FROM penyewaan WHERE id = %s"
        result = self.db_manager.execute_query(query, (id,), fetch=True)
        
        if result:
            data = result[0]
            return Penyewaan(
                id=data['id'],
                mobil_id=data['mobil_id'],
                pelanggan_id=data['pelanggan_id'],
                tanggal_sewa=data['tanggal_sewa'],
                tanggal_kembali=data['tanggal_kembali'],
                tanggal_pengembalian=data['tanggal_pengembalian'],
                total_hari=data['total_hari'],
                total_biaya=float(data['total_biaya']),
                denda=float(data['denda']),
                status=data['status'],
                kode_penyewaan=data['kode_penyewaan'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
        return None
    
    def find_all(self) -> List[Penyewaan]:
        query = "SELECT * FROM penyewaan"
        results = self.db_manager.execute_query(query, fetch=True)
        
        penyewaans = []
        for data in results:
            penyewaan = Penyewaan(
                id=data['id'],
                mobil_id=data['mobil_id'],
                pelanggan_id=data['pelanggan_id'],
                tanggal_sewa=data['tanggal_sewa'],
                tanggal_kembali=data['tanggal_kembali'],
                tanggal_pengembalian=data['tanggal_pengembalian'],
                total_hari=data['total_hari'],
                total_biaya=float(data['total_biaya']),
                denda=float(data['denda']),
                status=data['status'],
                kode_penyewaan=data['kode_penyewaan'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            penyewaans.append(penyewaan)
        return penyewaans
    
    def update(self, penyewaan: Penyewaan) -> bool:
        penyewaan.validate()
        query = """
        UPDATE penyewaan 
        SET mobil_id = %s, pelanggan_id = %s, tanggal_sewa = %s, 
            tanggal_kembali = %s, tanggal_pengembalian = %s, 
            total_hari = %s, total_biaya = %s, denda = %s, status = %s
        WHERE id = %s
        """
        params = (penyewaan.mobil_id, penyewaan.pelanggan_id,
                 penyewaan.tanggal_sewa, penyewaan.tanggal_kembali,
                 penyewaan.tanggal_pengembalian, penyewaan.total_hari,
                 penyewaan.total_biaya, penyewaan.denda, 
                 penyewaan.status, penyewaan.id)
        
        rows_affected = self.db_manager.execute_query(query, params)
        return rows_affected > 0
    
    def delete(self, id: int) -> bool:
        query = "DELETE FROM penyewaan WHERE id = %s"
        rows_affected = self.db_manager.execute_query(query, (id,))
        return rows_affected > 0
    
    def find_active_rentals(self) -> List[Penyewaan]:
        """Mencari penyewaan yang masih aktif"""
        query = "SELECT * FROM penyewaan WHERE status = 'aktif'"
        results = self.db_manager.execute_query(query, fetch=True)
        
        penyewaans = []
        for data in results:
            penyewaan = Penyewaan(
                id=data['id'],
                mobil_id=data['mobil_id'],
                pelanggan_id=data['pelanggan_id'],
                tanggal_sewa=data['tanggal_sewa'],
                tanggal_kembali=data['tanggal_kembali'],
                tanggal_pengembalian=data['tanggal_pengembalian'],
                total_hari=data['total_hari'],
                total_biaya=float(data['total_biaya']),
                denda=float(data['denda']),
                status=data['status'],
                kode_penyewaan=data['kode_penyewaan'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            penyewaans.append(penyewaan)
        return penyewaans
    
    def find_by_customer(self, pelanggan_id: int) -> List[Penyewaan]:
        """Mencari penyewaan berdasarkan pelanggan"""
        query = "SELECT * FROM penyewaan WHERE pelanggan_id = %s"
        results = self.db_manager.execute_query(query, (pelanggan_id,), fetch=True)
        
        penyewaans = []
        for data in results:
            penyewaan = Penyewaan(
                id=data['id'],
                mobil_id=data['mobil_id'],
                pelanggan_id=data['pelanggan_id'],
                tanggal_sewa=data['tanggal_sewa'],
                tanggal_kembali=data['tanggal_kembali'],
                tanggal_pengembalian=data['tanggal_pengembalian'],
                total_hari=data['total_hari'],
                total_biaya=float(data['total_biaya']),
                denda=float(data['denda']),
                status=data['status'],
                kode_penyewaan=data['kode_penyewaan'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            penyewaans.append(penyewaan)
        return penyewaans

class PembayaranRepository(Repository[Pembayaran]):
    """Repository untuk entity Pembayaran"""
    
    def create(self, pembayaran: Pembayaran) -> int:
        pembayaran.validate()
        query = """
        INSERT INTO pembayaran 
        (penyewaan_id, jumlah, metode_pembayaran, status, bukti_pembayaran)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (pembayaran.penyewaan_id, pembayaran.jumlah,
                 pembayaran.metode_pembayaran, pembayaran.status,
                 pembayaran.bukti_pembayaran)
        
        result = self.db_manager.execute_query(query, params, fetch=True)
        return result
    
    def find_by_id(self, id: int) -> Optional[Pembayaran]:
        query = "SELECT * FROM pembayaran WHERE id = %s"
        result = self.db_manager.execute_query(query, (id,), fetch=True)
        
        if result:
            data = result[0]
            return Pembayaran(
                id=data['id'],
                penyewaan_id=data['penyewaan_id'],
                jumlah=float(data['jumlah']),
                metode_pembayaran=data['metode_pembayaran'],
                status=data['status'],
                bukti_pembayaran=data['bukti_pembayaran'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
        return None
    
    def find_all(self) -> List[Pembayaran]:
        query = "SELECT * FROM pembayaran"
        results = self.db_manager.execute_query(query, fetch=True)
        
        pembayarans = []
        for data in results:
            pembayaran = Pembayaran(
                id=data['id'],
                penyewaan_id=data['penyewaan_id'],
                jumlah=float(data['jumlah']),
                metode_pembayaran=data['metode_pembayaran'],
                status=data['status'],
                bukti_pembayaran=data['bukti_pembayaran'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            pembayarans.append(pembayaran)
        return pembayarans
    
    def update(self, pembayaran: Pembayaran) -> bool:
        pembayaran.validate()
        query = """
        UPDATE pembayaran 
        SET penyewaan_id = %s, jumlah = %s, metode_pembayaran = %s, 
            status = %s, bukti_pembayaran = %s
        WHERE id = %s
        """
        params = (pembayaran.penyewaan_id, pembayaran.jumlah,
                 pembayaran.metode_pembayaran, pembayaran.status,
                 pembayaran.bukti_pembayaran, pembayaran.id)
        
        rows_affected = self.db_manager.execute_query(query, params)
        return rows_affected > 0
    
    def delete(self, id: int) -> bool:
        query = "DELETE FROM pembayaran WHERE id = %s"
        rows_affected = self.db_manager.execute_query(query, (id,))
        return rows_affected > 0
    
    def find_by_rental(self, penyewaan_id: int) -> List[Pembayaran]:
        """Mencari pembayaran berdasarkan penyewaan"""
        query = "SELECT * FROM pembayaran WHERE penyewaan_id = %s"
        results = self.db_manager.execute_query(query, (penyewaan_id,), fetch=True)
        
        pembayarans = []
        for data in results:
            pembayaran = Pembayaran(
                id=data['id'],
                penyewaan_id=data['penyewaan_id'],
                jumlah=float(data['jumlah']),
                metode_pembayaran=data['metode_pembayaran'],
                status=data['status'],
                bukti_pembayaran=data['bukti_pembayaran'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            pembayarans.append(pembayaran)
        return pembayarans