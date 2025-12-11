"""
Versi sederhana untuk setup database dengan sekali jalan
"""

import mysql.connector
from mysql.connector import Error
import sys

def setup_database_simple():
    """Setup database dengan cara sederhana"""
    
    print("Setup Database Rental Mobil - Simple Version")
    print("-" * 50)
    
    # Konfigurasi database
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',  # Kosongkan jika tidak ada password
        'database': 'rental_mobil_db'
    }
    
    try:
        # Step 1: Koneksi tanpa database
        print("1. Menghubungkan ke MySQL server...")
        connection = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password']
        )
        cursor = connection.cursor()
        
        # Step 2: Buat database
        print("2. Membuat database...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']} "
                      f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {config['database']}")
        
        # Step 3: Buat tabel
        print("3. Membuat tabel-tabel...")
        
        # SQL untuk membuat semua tabel
        sql_commands = [
            # Tabel mobil
            """
            DROP TABLE IF EXISTS mobil;
            CREATE TABLE mobil (
                id INT PRIMARY KEY AUTO_INCREMENT,
                merk VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                tahun INT NOT NULL,
                plat_nomor VARCHAR(20) UNIQUE NOT NULL,
                harga_sewa_per_hari DECIMAL(10,2) NOT NULL,
                status ENUM('tersedia', 'disewa', 'perbaikan') DEFAULT 'tersedia',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            
            # Tabel pelanggan
            """
            DROP TABLE IF EXISTS pelanggan;
            CREATE TABLE pelanggan (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nik VARCHAR(20) UNIQUE NOT NULL,
                nama VARCHAR(100) NOT NULL,
                alamat TEXT,
                no_telepon VARCHAR(15),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            
            # Tabel penyewaan
            """
            DROP TABLE IF EXISTS penyewaan;
            CREATE TABLE penyewaan (
                id INT PRIMARY KEY AUTO_INCREMENT,
                mobil_id INT NOT NULL,
                pelanggan_id INT NOT NULL,
                tanggal_sewa DATE NOT NULL,
                tanggal_kembali DATE NOT NULL,
                tanggal_pengembalian DATE,
                total_hari INT NOT NULL,
                total_biaya DECIMAL(12,2) NOT NULL,
                denda DECIMAL(10,2) DEFAULT 0,
                status ENUM('aktif', 'selesai', 'terlambat', 'batal') DEFAULT 'aktif',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (mobil_id) REFERENCES mobil(id),
                FOREIGN KEY (pelanggan_id) REFERENCES pelanggan(id)
            )
            """,
            
            # Tabel pembayaran
            """
            DROP TABLE IF EXISTS pembayaran;
            CREATE TABLE pembayaran (
                id INT PRIMARY KEY AUTO_INCREMENT,
                penyewaan_id INT NOT NULL,
                jumlah DECIMAL(12,2) NOT NULL,
                metode_pembayaran ENUM('tunai', 'transfer', 'kartu_kredit') NOT NULL,
                status ENUM('pending', 'lunas', 'gagal') DEFAULT 'pending',
                tanggal_bayar TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bukti_pembayaran TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (penyewaan_id) REFERENCES penyewaan(id)
            )
            """
        ]
        
        # Eksekusi semua perintah SQL
        for i, sql in enumerate(sql_commands, 1):
            cursor.execute(sql)
            print(f"   Tabel {i} berhasil dibuat")
        
        # Step 4: Insert sample data
        print("4. Memasukkan data contoh...")
        
        # Data mobil
        cursor.execute("""
        INSERT INTO mobil (merk, model, tahun, plat_nomor, harga_sewa_per_hari, status) VALUES
        ('Toyota', 'Avanza', 2022, 'B 1234 ABC', 300000, 'tersedia'),
        ('Honda', 'Brio', 2021, 'B 5678 DEF', 250000, 'tersedia'),
        ('Mitsubishi', 'Xpander', 2023, 'B 9012 GHI', 400000, 'tersedia'),
        ('Suzuki', 'Ertiga', 2020, 'B 3456 JKL', 280000, 'disewa'),
        ('Toyota', 'Fortuner', 2022, 'B 7890 MNO', 600000, 'tersedia')
        """)
        
        # Data pelanggan
        cursor.execute("""
        INSERT INTO pelanggan (nik, nama, alamat, no_telepon, email) VALUES
        ('1234567890123456', 'Budi Santoso', 'Jl. Merdeka No. 1', '081234567890', 'budi@email.com'),
        ('2345678901234567', 'Siti Rahayu', 'Jl. Sudirman No. 45', '082345678901', 'siti@email.com'),
        ('3456789012345678', 'Ahmad Wijaya', 'Jl. Thamrin No. 12', '083456789012', 'ahmad@email.com')
        """)
        
        # Data penyewaan (contoh)
        # Ambil ID mobil Suzuki Ertiga yang status disewa
        cursor.execute("SELECT id FROM mobil WHERE plat_nomor = 'B 3456 JKL'")
        mobil_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM pelanggan WHERE nik = '1234567890123456'")
        pelanggan_id = cursor.fetchone()[0]
        
        cursor.execute("""
        INSERT INTO penyewaan (mobil_id, pelanggan_id, tanggal_sewa, tanggal_kembali, 
                              total_hari, total_biaya, status) VALUES
        (%s, %s, '2024-03-01', '2024-03-05', 4, 1120000, 'aktif')
        """, (mobil_id, pelanggan_id))
        
        # Commit changes
        connection.commit()
        
        print("\n" + "="*50)
        print("SETUP BERHASIL!")
        print("="*50)
        print("\nTabel yang dibuat:")
        print("1. mobil      - Data kendaraan")
        print("2. pelanggan  - Data customer")
        print("3. penyewaan  - Transaksi rental (Tabel utama)")
        print("4. pembayaran - Transaksi pembayaran")
        
        # Tampilkan jumlah data
        cursor.execute("SELECT COUNT(*) FROM mobil")
        mobil_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pelanggan")
        pelanggan_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM penyewaan")
        penyewaan_count = cursor.fetchone()[0]
        
        print(f"\nData yang dimasukkan:")
        print(f"- {mobil_count} mobil")
        print(f"- {pelanggan_count} pelanggan")
        print(f"- {penyewaan_count} transaksi penyewaan")
        
        print("\nDatabase siap digunakan!")
        
    except Error as e:
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


def setup_database():
    """Wrapper function untuk setup database"""
    setup_database_simple()


if __name__ == "__main__":
    setup_database_simple()