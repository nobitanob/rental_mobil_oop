from datetime import date, timedelta
from typing import Dict, Optional, Tuple, List
from models.entitas import Mobil, Pelanggan, Penyewaan, Pembayaran
from models.repositories import (
    MobilRepository, PelangganRepository, 
    PenyewaanRepository, PembayaranRepository
)
from utils.validators import Validator

class RentalService:
    """Service untuk bisnis logic rental mobil (Single Responsibility)"""
    
    def __init__(self, mobil_repo: MobilRepository, 
                 pelanggan_repo: PelangganRepository,
                 penyewaan_repo: PenyewaanRepository,
                 pembayaran_repo: PembayaranRepository):
        self.mobil_repo = mobil_repo
        self.pelanggan_repo = pelanggan_repo
        self.penyewaan_repo = penyewaan_repo
        self.pembayaran_repo = pembayaran_repo
    
    def _generate_rental_code(self) -> str:
        """Generate unique rental code"""
        from datetime import datetime
        year_month = datetime.now().strftime('%Y%m')
        prefix = f"RENT-{year_month}-"
        
        # Get all existing rentals for this month and all months
        all_rentals = self.penyewaan_repo.find_all()
        max_seq = 0
        
        if all_rentals:
            for r in all_rentals:
                if r.kode_penyewaan:
                    # Extract sequence number from code like "RENT-202512-0001" or "RENT-202512-0000"
                    try:
                        # Split by hyphen to get parts
                        parts = r.kode_penyewaan.split('-')
                        if len(parts) >= 3:
                            # Last part is the sequence number
                            seq_str = parts[-1]
                            seq_num = int(seq_str)
                            if seq_num > max_seq:
                                max_seq = seq_num
                    except (ValueError, AttributeError, IndexError):
                        pass
        
        # Get next sequence number (always increment globally)
        next_seq = max_seq + 1
        
        return f"RENT-{year_month}-{next_seq:04d}"
    
    def sewa_mobil(self, mobil_id: int, pelanggan_id: int, 
                   tanggal_sewa: date, jumlah_hari: int) -> Tuple[bool, str, Optional[int]]:
        """
        Proses penyewaan mobil
        Returns: (success, message, rental_id)
        """
        try:
            # Validasi input
            Validator.validate_positive_number(jumlah_hari, "Jumlah hari")
            Validator.validate_date_not_past(tanggal_sewa)
            
            # Cek ketersediaan mobil
            mobil = self.mobil_repo.find_by_id(mobil_id)
            if not mobil:
                return False, "Mobil tidak ditemukan", None
            
            if mobil.status != 'tersedia':
                return False, f"Mobil sedang {mobil.status}", None
            
            # Cek pelanggan
            pelanggan = self.pelanggan_repo.find_by_id(pelanggan_id)
            if not pelanggan:
                return False, "Pelanggan tidak ditemukan", None
            
            # Hitung biaya
            tanggal_kembali = tanggal_sewa + timedelta(days=jumlah_hari)
            total_biaya = mobil.harga_sewa_per_hari * jumlah_hari
            
            # Generate rental code
            kode_penyewaan = self._generate_rental_code()
            
            # Buat penyewaan
            penyewaan = Penyewaan(
                mobil_id=mobil_id,
                pelanggan_id=pelanggan_id,
                tanggal_sewa=tanggal_sewa,
                tanggal_kembali=tanggal_kembali,
                total_hari=jumlah_hari,
                total_biaya=total_biaya,
                status='aktif',
                kode_penyewaan=kode_penyewaan
            )
            
            penyewaan_id = self.penyewaan_repo.create(penyewaan)
            
            # Update status mobil
            self.mobil_repo.update_status(mobil_id, 'disewa')
            
            return True, f"Penyewaan berhasil. Kode: {kode_penyewaan}. Total biaya: Rp {total_biaya:,.2f}", penyewaan_id
            
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    def pengembalian_mobil(self, penyewaan_id: int, 
                          tanggal_pengembalian: date) -> Tuple[bool, str, float]:
        """
        Proses pengembalian mobil
        Returns: (success, message, denda)
        """
        try:
            # Cek penyewaan
            penyewaan = self.penyewaan_repo.find_by_id(penyewaan_id)
            if not penyewaan:
                return False, "Penyewaan tidak ditemukan", 0
            
            if penyewaan.status != 'aktif':
                return False, f"Penyewaan sudah {penyewaan.status}", 0
            
            # Hitung keterlambatan
            hari_keterlambatan = max(0, (tanggal_pengembalian - penyewaan.tanggal_kembali).days)
            
            # Hitung denda jika telat
            mobil = self.mobil_repo.find_by_id(penyewaan.mobil_id)
            denda = 0
            status = 'selesai'
            
            if hari_keterlambatan > 0:
                denda = penyewaan.hitung_denda(mobil.harga_sewa_per_hari, hari_keterlambatan)
                status = 'terlambat'
            
            # Update penyewaan
            penyewaan.tanggal_pengembalian = tanggal_pengembalian
            penyewaan.denda = denda
            penyewaan.status = status
            self.penyewaan_repo.update(penyewaan)
            
            # Update status mobil
            self.mobil_repo.update_status(penyewaan.mobil_id, 'tersedia')
            
            total_bayar = penyewaan.total_biaya + denda
            message = f"Pengembalian berhasil. "
            if denda > 0:
                message += f"Denda keterlambatan {hari_keterlambatan} hari: Rp {denda:,.2f}. "
            message += f"Total yang harus dibayar: Rp {total_bayar:,.2f}"
            
            return True, message, denda
            
        except Exception as e:
            return False, f"Error: {str(e)}", 0
    
    def bayar_sewa(self, penyewaan_id: int, jumlah: float, 
                   metode_pembayaran: str) -> Tuple[bool, str]:
        """
        Proses pembayaran sewa
        """
        try:
            # Cek penyewaan
            penyewaan = self.penyewaan_repo.find_by_id(penyewaan_id)
            if not penyewaan:
                return False, "Penyewaan tidak ditemukan"
            
            total_bayar = penyewaan.total_biaya + penyewaan.denda
            
            # Validasi jumlah pembayaran
            if jumlah < total_bayar:
                return False, f"Jumlah pembayaran kurang. Total yang harus dibayar: Rp {total_bayar:,.2f}"
            
            # Buat pembayaran
            pembayaran = Pembayaran(
                penyewaan_id=penyewaan_id,
                jumlah=jumlah,
                metode_pembayaran=metode_pembayaran,
                status='lunas'
            )
            
            self.pembayaran_repo.create(pembayaran)
            
            # Jika ada kembalian
            kembalian = jumlah - total_bayar
            message = f"Pembayaran berhasil. "
            if kembalian > 0:
                message += f"Kembalian: Rp {kembalian:,.2f}"
            
            return True, message
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def laporan_penyewaan_harian(self, tanggal: date) -> Dict:
        """
        Generate laporan penyewaan harian
        """
        try:
            # Query untuk laporan
            query = """
            SELECT 
                p.id,
                p.tanggal_sewa,
                p.tanggal_kembali,
                p.total_biaya,
                p.denda,
                m.merk,
                m.model,
                m.plat_nomor,
                pl.nama as nama_pelanggan
            FROM penyewaan p
            JOIN mobil m ON p.mobil_id = m.id
            JOIN pelanggan pl ON p.pelanggan_id = pl.id
            WHERE DATE(p.tanggal_sewa) = %s
            ORDER BY p.tanggal_sewa
            """
            
            # Execute query
            from database.connection import DatabaseManager
            db_manager = DatabaseManager()
            results = db_manager.execute_query(query, (tanggal,), fetch=True)
            
            # Hitung total
            total_biaya = sum(float(r['total_biaya']) for r in results)
            total_denda = sum(float(r['denda']) for r in results)
            total_pendapatan = total_biaya + total_denda
            
            return {
                'tanggal': tanggal,
                'total_transaksi': len(results),
                'total_biaya': total_biaya,
                'total_denda': total_denda,
                'total_pendapatan': total_pendapatan,
                'transaksi': results
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def cari_mobil_tersedia(self, merk: Optional[str] = None, 
                           harga_max: Optional[float] = None) -> List[Mobil]:
        """
        Cari mobil tersedia dengan filter
        """
        mobils = self.mobil_repo.find_available()
        
        # Apply filters
        filtered_mobils = []
        for mobil in mobils:
            if merk and merk.lower() not in mobil.merk.lower():
                continue
            if harga_max and mobil.harga_sewa_per_hari > harga_max:
                continue
            filtered_mobils.append(mobil)
        
        return filtered_mobils