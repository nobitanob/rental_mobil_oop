import sys
from datetime import date, timedelta
from database.connection import DatabaseManager
from database.setup_database import setup_database
from models.repositories import (
    MobilRepository, PelangganRepository,
    PenyewaanRepository, PembayaranRepository
)
from services.rental_service import RentalService
from models.entitas import Mobil, Pelanggan

class RentalMobilApp:
    """Aplikasi utama rental mobil"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.init_repositories()
        self.rental_service = RentalService(
            self.mobil_repo, self.pelanggan_repo,
            self.penyewaan_repo, self.pembayaran_repo
        )
    
    def init_repositories(self):
        """Initialize semua repositories"""
        self.mobil_repo = MobilRepository(self.db_manager)
        self.pelanggan_repo = PelangganRepository(self.db_manager)
        self.penyewaan_repo = PenyewaanRepository(self.db_manager)
        self.pembayaran_repo = PembayaranRepository(self.db_manager)
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("SISTEM RENTAL MOBIL OOP")
        print("="*50)
        print("1. Kelola Mobil")
        print("2. Kelola Pelanggan")
        print("3. Sewa Mobil")
        print("4. Pengembalian Mobil")
        print("5. Pembayaran")
        print("6. Laporan Harian")
        print("7. Cari Mobil Tersedia")
        print("8. Setup Database")
        print("0. Keluar")
        print("="*50)
    
    def run(self):
        """Run aplikasi"""
        while True:
            self.display_menu()
            choice = input("Pilih menu (0-8): ").strip()
            
            if choice == '1':
                self.kelola_mobil()
            elif choice == '2':
                self.kelola_pelanggan()
            elif choice == '3':
                self.sewa_mobil_menu()
            elif choice == '4':
                self.pengembalian_mobil_menu()
            elif choice == '5':
                self.pembayaran_menu()
            elif choice == '6':
                self.laporan_harian_menu()
            elif choice == '7':
                self.cari_mobil_tersedia_menu()
            elif choice == '8':
                self.setup_database_menu()
            elif choice == '0':
                print("Terima kasih telah menggunakan sistem rental mobil!")
                break
            else:
                print("Pilihan tidak valid!")
    
    def kelola_mobil(self):
        """Menu kelola mobil"""
        print("\n" + "-"*30)
        print("KELOLA MOBIL")
        print("-"*30)
        print("1. Tambah Mobil")
        print("2. Lihat Semua Mobil")
        print("3. Lihat Mobil Tersedia")
        print("4. Update Mobil")
        print("5. Hapus Mobil")
        print("0. Kembali")
        
        choice = input("Pilih (0-5): ").strip()
        
        if choice == '1':
            self.tambah_mobil()
        elif choice == '2':
            self.lihat_semua_mobil()
        elif choice == '3':
            self.lihat_mobil_tersedia()
        elif choice == '4':
            self.update_mobil()
        elif choice == '5':
            self.hapus_mobil()
    
    def tambah_mobil(self):
        """Tambah mobil baru"""
        print("\n--- Tambah Mobil ---")
        try:
            merk = input("Merk: ").strip()
            model = input("Model: ").strip()
            tahun = int(input("Tahun: ").strip())
            plat_nomor = input("Plat Nomor: ").strip()
            harga = float(input("Harga Sewa per Hari: ").strip())
            
            mobil = Mobil(
                merk=merk,
                model=model,
                tahun=tahun,
                plat_nomor=plat_nomor,
                harga_sewa_per_hari=harga
            )
            
            mobil_id = self.mobil_repo.create(mobil)
            print(f"Mobil berhasil ditambahkan dengan ID: {mobil_id}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    def lihat_semua_mobil(self):
        """Lihat semua mobil"""
        print("\n--- Daftar Semua Mobil ---")
        mobils = self.mobil_repo.find_all()
        
        if not mobils:
            print("Tidak ada data mobil.")
            return
        
        print(f"{'ID':<5} {'Merk/Model':<20} {'Tahun':<6} {'Plat':<12} {'Harga/Hari':<12} {'Status':<10}")
        print("-"*70)
        for mobil in mobils:
            print(f"{mobil.id:<5} {mobil.merk} {mobil.model:<14} {mobil.tahun:<6} "
                  f"{mobil.plat_nomor:<12} Rp {mobil.harga_sewa_per_hari:<10,.0f} {mobil.status:<10}")
    
    def lihat_mobil_tersedia(self):
        """Lihat mobil yang tersedia"""
        print("\n--- Daftar Mobil Tersedia ---")
        mobils = self.mobil_repo.find_available()
        
        if not mobils:
            print("Tidak ada mobil tersedia.")
            return
        
        print(f"{'ID':<5} {'Merk/Model':<20} {'Tahun':<6} {'Plat':<12} {'Harga/Hari':<12}")
        print("-"*55)
        for mobil in mobils:
            print(f"{mobil.id:<5} {mobil.merk} {mobil.model:<14} {mobil.tahun:<6} "
                  f"{mobil.plat_nomor:<12} Rp {mobil.harga_sewa_per_hari:<10,.0f}")
    
    def update_mobil(self):
        """Update data mobil"""
        self.lihat_semua_mobil()
        try:
            mobil_id = int(input("\nID Mobil yang akan diupdate: ").strip())
            mobil = self.mobil_repo.find_by_id(mobil_id)
            
            if not mobil:
                print("Mobil tidak ditemukan.")
                return
            
            print(f"\nUpdate Mobil: {mobil}")
            print("Kosongkan jika tidak ingin mengubah")
            
            merk = input(f"Merk [{mobil.merk}]: ").strip() or mobil.merk
            model = input(f"Model [{mobil.model}]: ").strip() or mobil.model
            tahun = input(f"Tahun [{mobil.tahun}]: ").strip()
            tahun = int(tahun) if tahun else mobil.tahun
            plat_nomor = input(f"Plat Nomor [{mobil.plat_nomor}]: ").strip() or mobil.plat_nomor
            harga = input(f"Harga Sewa [{mobil.harga_sewa_per_hari}]: ").strip()
            harga = float(harga) if harga else mobil.harga_sewa_per_hari
            status = input(f"Status [{mobil.status}]: ").strip() or mobil.status
            
            mobil.merk = merk
            mobil.model = model
            mobil.tahun = tahun
            mobil.plat_nomor = plat_nomor
            mobil.harga_sewa_per_hari = harga
            mobil.status = status
            
            if self.mobil_repo.update(mobil):
                print("Mobil berhasil diupdate.")
            else:
                print("Gagal mengupdate mobil.")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def hapus_mobil(self):
        """Hapus mobil"""
        self.lihat_semua_mobil()
        try:
            mobil_id = int(input("\nID Mobil yang akan dihapus: ").strip())
            
            confirm = input(f"Yakin ingin menghapus mobil ID {mobil_id}? (y/n): ").strip().lower()
            if confirm == 'y':
                if self.mobil_repo.delete(mobil_id):
                    print("Mobil berhasil dihapus.")
                else:
                    print("Gagal menghapus mobil atau mobil tidak ditemukan.")
                    
        except Exception as e:
            print(f"Error: {e}")
    
    def kelola_pelanggan(self):
        """Menu kelola pelanggan"""
        print("\n" + "-"*30)
        print("KELOLA PELANGGAN")
        print("-"*30)
        print("1. Tambah Pelanggan")
        print("2. Lihat Semua Pelanggan")
        print("3. Update Pelanggan")
        print("4. Hapus Pelanggan")
        print("0. Kembali")
        
        choice = input("Pilih (0-4): ").strip()
        
        if choice == '1':
            self.tambah_pelanggan()
        elif choice == '2':
            self.lihat_semua_pelanggan()
        elif choice == '3':
            self.update_pelanggan()
        elif choice == '4':
            self.hapus_pelanggan()
    
    def tambah_pelanggan(self):
        """Tambah pelanggan baru"""
        print("\n--- Tambah Pelanggan ---")
        try:
            nik = input("NIK (16 digit): ").strip()
            nama = input("Nama: ").strip()
            alamat = input("Alamat: ").strip()
            no_telepon = input("No. Telepon: ").strip()
            email = input("Email: ").strip()
            
            pelanggan = Pelanggan(
                nik=nik,
                nama=nama,
                alamat=alamat,
                no_telepon=no_telepon,
                email=email
            )
            
            pelanggan_id = self.pelanggan_repo.create(pelanggan)
            print(f"Pelanggan berhasil ditambahkan dengan ID: {pelanggan_id}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    def lihat_semua_pelanggan(self):
        """Lihat semua pelanggan"""
        print("\n--- Daftar Semua Pelanggan ---")
        pelanggans = self.pelanggan_repo.find_all()
        
        if not pelanggans:
            print("Tidak ada data pelanggan.")
            return
        
        print(f"{'ID':<5} {'NIK':<20} {'Nama':<20} {'No. Telp':<15} {'Email':<20}")
        print("-"*80)
        for pelanggan in pelanggans:
            print(f"{pelanggan.id:<5} {pelanggan.nik:<20} {pelanggan.nama:<20} "
                  f"{pelanggan.no_telepon:<15} {pelanggan.email:<20}")
    
    def update_pelanggan(self):
        """Update data pelanggan"""
        self.lihat_semua_pelanggan()
        try:
            pelanggan_id = int(input("\nID Pelanggan yang akan diupdate: ").strip())
            pelanggan = self.pelanggan_repo.find_by_id(pelanggan_id)
            
            if not pelanggan:
                print("Pelanggan tidak ditemukan.")
                return
            
            print(f"\nUpdate Pelanggan: {pelanggan}")
            print("Kosongkan jika tidak ingin mengubah")
            
            nik = input(f"NIK [{pelanggan.nik}]: ").strip() or pelanggan.nik
            nama = input(f"Nama [{pelanggan.nama}]: ").strip() or pelanggan.nama
            alamat = input(f"Alamat [{pelanggan.alamat}]: ").strip() or pelanggan.alamat
            no_telepon = input(f"No. Telepon [{pelanggan.no_telepon}]: ").strip() or pelanggan.no_telepon
            email = input(f"Email [{pelanggan.email}]: ").strip() or pelanggan.email
            
            pelanggan.nik = nik
            pelanggan.nama = nama
            pelanggan.alamat = alamat
            pelanggan.no_telepon = no_telepon
            pelanggan.email = email
            
            if self.pelanggan_repo.update(pelanggan):
                print("Pelanggan berhasil diupdate.")
            else:
                print("Gagal mengupdate pelanggan.")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def hapus_pelanggan(self):
        """Hapus pelanggan"""
        self.lihat_semua_pelanggan()
        try:
            pelanggan_id = int(input("\nID Pelanggan yang akan dihapus: ").strip())
            
            confirm = input(f"Yakin ingin menghapus pelanggan ID {pelanggan_id}? (y/n): ").strip().lower()
            if confirm == 'y':
                if self.pelanggan_repo.delete(pelanggan_id):
                    print("Pelanggan berhasil dihapus.")
                else:
                    print("Gagal menghapus pelanggan atau pelanggan tidak ditemukan.")
                    
        except Exception as e:
            print(f"Error: {e}")
    
    def sewa_mobil_menu(self):
        """Menu sewa mobil"""
        print("\n--- Sewa Mobil ---")
        
        # Tampilkan mobil tersedia
        mobils = self.mobil_repo.find_available()
        if not mobils:
            print("Tidak ada mobil tersedia.")
            return
        
        print("\nDaftar Mobil Tersedia:")
        self.lihat_mobil_tersedia()
        
        # Tampilkan pelanggan
        pelanggans = self.pelanggan_repo.find_all()
        if not pelanggans:
            print("Tidak ada data pelanggan. Silakan tambah pelanggan terlebih dahulu.")
            return
        
        print("\nDaftar Pelanggan:")
        self.lihat_semua_pelanggan()
        
        try:
            mobil_id = int(input("\nID Mobil yang akan disewa: ").strip())
            pelanggan_id = int(input("ID Pelanggan: ").strip())
            jumlah_hari = int(input("Jumlah Hari: ").strip())
            
            # Default tanggal sewa hari ini
            tanggal_sewa = date.today()
            
            success, message, rental_id = self.rental_service.sewa_mobil(
                mobil_id, pelanggan_id, tanggal_sewa, jumlah_hari
            )
            
            print(f"\n{message}")
            if success:
                print(f"ID Penyewaan: {rental_id}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def pengembalian_mobil_menu(self):
        """Menu pengembalian mobil"""
        print("\n--- Pengembalian Mobil ---")
        
        try:
            rental_id = int(input("ID Penyewaan: ").strip())
            
            # Default tanggal pengembalian hari ini
            tanggal_pengembalian = date.today()
            
            success, message, denda = self.rental_service.pengembalian_mobil(
                rental_id, tanggal_pengembalian
            )
            
            print(f"\n{message}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    def pembayaran_menu(self):
        """Menu pembayaran"""
        print("\n--- Pembayaran ---")
        
        try:
            rental_id = int(input("ID Penyewaan: ").strip())
            jumlah = float(input("Jumlah Bayar: ").strip())
            
            print("\nMetode Pembayaran:")
            print("1. Tunai")
            print("2. Transfer")
            print("3. Kartu Kredit")
            
            metode_choice = input("Pilih metode (1-3): ").strip()
            metode_map = {'1': 'tunai', '2': 'transfer', '3': 'kartu_kredit'}
            metode = metode_map.get(metode_choice, 'tunai')
            
            success, message = self.rental_service.bayar_sewa(
                rental_id, jumlah, metode
            )
            
            print(f"\n{message}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    def laporan_harian_menu(self):
        """Menu laporan harian"""
        print("\n--- Laporan Harian ---")
        
        try:
            tanggal_str = input("Tanggal (YYYY-MM-DD) [kosongkan untuk hari ini]: ").strip()
            if tanggal_str:
                tanggal = date.fromisoformat(tanggal_str)
            else:
                tanggal = date.today()
            
            laporan = self.rental_service.laporan_penyewaan_harian(tanggal)
            
            if 'error' in laporan:
                print(f"Error: {laporan['error']}")
                return
            
            print(f"\nLaporan Penyewaan Tanggal: {tanggal}")
            print(f"Total Transaksi: {laporan['total_transaksi']}")
            print(f"Total Biaya Sewa: Rp {laporan['total_biaya']:,.2f}")
            print(f"Total Denda: Rp {laporan['total_denda']:,.2f}")
            print(f"Total Pendapatan: Rp {laporan['total_pendapatan']:,.2f}")
            print("-"*50)
            
            if laporan['transaksi']:
                print("\nDetail Transaksi:")
                for trans in laporan['transaksi']:
                    print(f"ID: {trans['id']} | {trans['merk']} {trans['model']} "
                          f"({trans['plat_nomor']}) | Pelanggan: {trans['nama_pelanggan']} | "
                          f"Biaya: Rp {float(trans['total_biaya']):,.2f}")
            else:
                print("Tidak ada transaksi pada tanggal ini.")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def cari_mobil_tersedia_menu(self):
        """Menu cari mobil tersedia"""
        print("\n--- Cari Mobil Tersedia ---")
        
        try:
            merk = input("Merk (kosongkan untuk semua): ").strip() or None
            harga_max_str = input("Harga Maksimal per Hari (kosongkan untuk semua): ").strip()
            harga_max = float(harga_max_str) if harga_max_str else None
            
            mobils = self.rental_service.cari_mobil_tersedia(merk, harga_max)
            
            if not mobils:
                print("Tidak ada mobil yang sesuai dengan kriteria.")
                return
            
            print(f"\nHasil Pencarian ({len(mobils)} mobil ditemukan):")
            print(f"{'ID':<5} {'Merk/Model':<20} {'Tahun':<6} {'Plat':<12} {'Harga/Hari':<12}")
            print("-"*55)
            for mobil in mobils:
                print(f"{mobil.id:<5} {mobil.merk} {mobil.model:<14} {mobil.tahun:<6} "
                      f"{mobil.plat_nomor:<12} Rp {mobil.harga_sewa_per_hari:<10,.0f}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def setup_database_menu(self):
        """Menu setup database"""
        print("\n--- Setup Database ---")
        print("PERINGATAN: Ini akan menghapus dan membuat ulang semua tabel!")
        
        confirm = input("Yakin ingin melanjutkan? (y/n): ").strip().lower()
        if confirm == 'y':
            try:
                setup_database()
                print("Database berhasil di-setup!")
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function"""
    print("Menyiapkan sistem rental mobil...")
    app = RentalMobilApp()
    
    # Check if database needs setup
    try:
        # Try to get available cars to test connection
        mobils = app.mobil_repo.find_all()
        print(f"Koneksi database berhasil. {len(mobils)} mobil ditemukan.")
    except:
        print("Database belum di-setup. Silakan pilih menu 8 untuk setup database.")
    
    app.run()

if __name__ == "__main__":
    main()