"""
CREATE DATABASE SISTEM RENTAL MOBIL
Script lengkap untuk membuat database, tabel, constraints, triggers, stored procedures,
dan memasukkan data contoh untuk sistem rental mobil.

Jalankan script ini sekali saja untuk setup awal database.
"""

import mysql.connector
from mysql.connector import Error
import getpass
import sys
from datetime import datetime, timedelta
import random

class DatabaseCreator:
    """Class untuk membuat dan menginisialisasi database rental mobil"""
    
    def __init__(self, host='localhost', user='root', password=None):
        """
        Inisialisasi DatabaseCreator
        
        Args:
            host: MySQL host (default: localhost)
            user: MySQL username (default: root)
            password: MySQL password
        """
        self.host = host
        self.user = user
        self.password = password
        self.database_name = 'rental_mobil_db'
        self.connection = None
        
        # Colors untuk output terminal
        self.COLORS = {
            'HEADER': '\033[95m',
            'OKBLUE': '\033[94m',
            'OKGREEN': '\033[92m',
            'WARNING': '\033[93m',
            'FAIL': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m'
        }
    
    def print_header(self, text):
        """Print header dengan formatting"""
        print(f"\n{self.COLORS['OKBLUE']}{'='*60}{self.COLORS['ENDC']}")
        print(f"{self.COLORS['HEADER']}{self.COLORS['BOLD']}{text}{self.COLORS['ENDC']}")
        print(f"{self.COLORS['OKBLUE']}{'='*60}{self.COLORS['ENDC']}")
    
    def print_success(self, text):
        """Print pesan success"""
        print(f"{self.COLORS['OKGREEN']}✓ {text}{self.COLORS['ENDC']}")
    
    def print_error(self, text):
        """Print pesan error"""
        print(f"{self.COLORS['FAIL']}✗ {text}{self.COLORS['ENDC']}")
    
    def print_warning(self, text):
        """Print pesan warning"""
        print(f"{self.COLORS['WARNING']}⚠ {text}{self.COLORS['ENDC']}")
    
    def print_info(self, text):
        """Print pesan info"""
        print(f"{self.COLORS['OKBLUE']}ℹ {text}{self.COLORS['ENDC']}")
    
    def connect_without_db(self):
        """Membuat koneksi tanpa database (untuk membuat database)"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            self.print_success(f"Berhasil terhubung ke MySQL server: {self.host}")
            return True
        except Error as e:
            self.print_error(f"Gagal terhubung ke MySQL server: {e}")
            if "Access denied" in str(e):
                self.print_info("Pastikan username dan password MySQL benar")
            elif "Can't connect" in str(e):
                self.print_info("Pastikan MySQL server sedang berjalan")
            return False
    
    def connect_with_db(self):
        """Membuat koneksi dengan database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database_name
            )
            self.print_success(f"Berhasil terhubung ke database: {self.database_name}")
            return True
        except Error as e:
            self.print_error(f"Gagal terhubung ke database: {e}")
            return False
    
    def create_database(self):
        """Membuat database jika belum ada"""
        cursor = self.connection.cursor()
        
        try:
            # Drop database jika sudah ada (opsional, hati-hati!)
            drop_db = input(f"\n{self.COLORS['WARNING']}Hapus database '{self.database_name}' jika sudah ada? (y/n): {self.COLORS['ENDC']}").strip().lower()
            
            if drop_db == 'y':
                cursor.execute(f"DROP DATABASE IF EXISTS {self.database_name}")
                self.print_warning(f"Database '{self.database_name}' dihapus (jika ada)")
            
            # Create database baru
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {self.database_name} 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci
            """)
            
            # Gunakan database
            cursor.execute(f"USE {self.database_name}")
            
            self.print_success(f"Database '{self.database_name}' berhasil dibuat")
            return True
            
        except Error as e:
            self.print_error(f"Gagal membuat database: {e}")
            return False
        finally:
            cursor.close()
    
    def create_tables(self):
        """Membuat semua tabel yang diperlukan"""
        cursor = self.connection.cursor()
        
        self.print_header("MEMBUAT TABEL-TABEL DATABASE")
        
        # Daftar query untuk membuat tabel
        table_queries = {
            'mobil': """
                CREATE TABLE IF NOT EXISTS mobil (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    merk VARCHAR(100) NOT NULL,
                    model VARCHAR(100) NOT NULL,
                    tahun INT NOT NULL,
                    plat_nomor VARCHAR(20) UNIQUE NOT NULL,
                    warna VARCHAR(50),
                    transmisi ENUM('manual', 'automatic', 'semi-automatic') DEFAULT 'manual',
                    bahan_bakar ENUM('bensin', 'solar', 'listrik', 'hybrid') DEFAULT 'bensin',
                    kapasitas_penumpang INT DEFAULT 5,
                    harga_sewa_per_hari DECIMAL(10,2) NOT NULL,
                    status ENUM('tersedia', 'disewa', 'perbaikan', 'nonaktif') DEFAULT 'tersedia',
                    deskripsi TEXT,
                    gambar_url VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    -- Indexes untuk optimasi query
                    INDEX idx_status (status),
                    INDEX idx_merk (merk),
                    INDEX idx_tahun (tahun),
                    INDEX idx_harga (harga_sewa_per_hari),
                    INDEX idx_plat (plat_nomor),
                    
                    -- Constraints
                    CHECK (tahun >= 1900 AND tahun <= 2099),
                    CHECK (harga_sewa_per_hari > 0),
                    CHECK (kapasitas_penumpang > 0)
                ) ENGINE=InnoDB
            """,
            
            'pelanggan': """
                CREATE TABLE IF NOT EXISTS pelanggan (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nik VARCHAR(20) UNIQUE NOT NULL,
                    nama VARCHAR(100) NOT NULL,
                    jenis_kelamin ENUM('L', 'P') DEFAULT 'L',
                    tanggal_lahir DATE,
                    alamat TEXT,
                    kota VARCHAR(100),
                    provinsi VARCHAR(100),
                    kode_pos VARCHAR(10),
                    no_telepon VARCHAR(15) NOT NULL,
                    email VARCHAR(100),
                    pekerjaan VARCHAR(100),
                    status_aktif ENUM('aktif', 'nonaktif', 'diblokir') DEFAULT 'aktif',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    -- Indexes
                    INDEX idx_nik (nik),
                    INDEX idx_nama (nama),
                    INDEX idx_email (email),
                    INDEX idx_telepon (no_telepon),
                    INDEX idx_status (status_aktif),
                    
                    -- Constraints
                    CHECK (LENGTH(nik) >= 16),
                    CONSTRAINT chk_email_format CHECK (email IS NULL OR email LIKE '%@%.%')
                ) ENGINE=InnoDB
            """,
            
            'penyewaan': """
                CREATE TABLE IF NOT EXISTS penyewaan (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    kode_penyewaan VARCHAR(20) UNIQUE NOT NULL,
                    mobil_id INT NOT NULL,
                    pelanggan_id INT NOT NULL,
                    tanggal_sewa DATETIME NOT NULL,
                    tanggal_kembali DATETIME NOT NULL,
                    tanggal_pengembalian DATETIME,
                    lokasi_penjemputan VARCHAR(255),
                    lokasi_pengembalian VARCHAR(255),
                    total_hari INT NOT NULL,
                    total_biaya DECIMAL(12,2) NOT NULL,
                    denda DECIMAL(10,2) DEFAULT 0,
                    status ENUM('pending', 'diproses', 'aktif', 'selesai', 'terlambat', 'batal') DEFAULT 'pending',
                    catatan TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    -- Foreign Keys dengan cascade
                    FOREIGN KEY (mobil_id) 
                        REFERENCES mobil(id) 
                        ON DELETE RESTRICT 
                        ON UPDATE CASCADE,
                        
                    FOREIGN KEY (pelanggan_id) 
                        REFERENCES pelanggan(id) 
                        ON DELETE RESTRICT 
                        ON UPDATE CASCADE,
                    
                    -- Indexes
                    INDEX idx_status (status),
                    INDEX idx_tanggal_sewa (tanggal_sewa),
                    INDEX idx_tanggal_kembali (tanggal_kembali),
                    INDEX idx_pelanggan (pelanggan_id),
                    INDEX idx_mobil (mobil_id),
                    INDEX idx_kode (kode_penyewaan),
                    
                    -- Constraints
                    CHECK (tanggal_kembali > tanggal_sewa),
                    CHECK (total_hari > 0),
                    CHECK (total_biaya > 0),
                    CHECK (denda >= 0),
                    CONSTRAINT chk_tanggal_pengembalian 
                        CHECK (tanggal_pengembalian IS NULL OR tanggal_pengembalian >= tanggal_sewa)
                ) ENGINE=InnoDB
            """,
            
            'pembayaran': """
                CREATE TABLE IF NOT EXISTS pembayaran (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    kode_pembayaran VARCHAR(20) UNIQUE NOT NULL,
                    penyewaan_id INT NOT NULL,
                    jumlah DECIMAL(12,2) NOT NULL,
                    metode_pembayaran ENUM('tunai', 'transfer', 'kartu_kredit', 'debit', 'e-wallet') NOT NULL,
                    status ENUM('pending', 'diproses', 'lunas', 'gagal', 'dibatalkan', 'refund') DEFAULT 'pending',
                    tanggal_bayar DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tanggal_konfirmasi DATETIME,
                    bank_tujuan VARCHAR(100),
                    no_rekening VARCHAR(50),
                    nama_rekening VARCHAR(100),
                    bukti_pembayaran TEXT,
                    keterangan TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    -- Foreign Key
                    FOREIGN KEY (penyewaan_id) 
                        REFERENCES penyewaan(id) 
                        ON DELETE CASCADE 
                        ON UPDATE CASCADE,
                    
                    -- Indexes
                    INDEX idx_status (status),
                    INDEX idx_tanggal_bayar (tanggal_bayar),
                    INDEX idx_penyewaan (penyewaan_id),
                    INDEX idx_metode (metode_pembayaran),
                    INDEX idx_kode (kode_pembayaran),
                    
                    -- Constraints
                    CHECK (jumlah > 0)
                ) ENGINE=InnoDB
            """,
            
            'pengembalian': """
                CREATE TABLE IF NOT EXISTS pengembalian (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    penyewaan_id INT NOT NULL,
                    tanggal_pengembalian DATETIME NOT NULL,
                    kondisi_mobil ENUM('baik', 'rusak_ringan', 'rusak_berat') DEFAULT 'baik',
                    catatan_kerusakan TEXT,
                    biaya_tambahan DECIMAL(10,2) DEFAULT 0,
                    km_akhir INT,
                    km_awal INT,
                    foto_kondisi TEXT,
                    dikembalikan_oleh VARCHAR(100),
                    diterima_oleh VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    -- Foreign Key
                    FOREIGN KEY (penyewaan_id) 
                        REFERENCES penyewaan(id) 
                        ON DELETE CASCADE 
                        ON UPDATE CASCADE,
                    
                    -- Indexes
                    INDEX idx_tanggal (tanggal_pengembalian),
                    INDEX idx_penyewaan (penyewaan_id),
                    
                    -- Constraints
                    CHECK (biaya_tambahan >= 0),
                    CHECK (km_akhir >= 0),
                    CHECK (km_awal >= 0)
                ) ENGINE=InnoDB
            """,
            
            'driver': """
                CREATE TABLE IF NOT EXISTS driver (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nik VARCHAR(20) UNIQUE NOT NULL,
                    nama VARCHAR(100) NOT NULL,
                    no_telepon VARCHAR(15) NOT NULL,
                    alamat TEXT,
                    tanggal_lahir DATE,
                    sim_nomor VARCHAR(50),
                    sim_jenis VARCHAR(50),
                    sim_expiry DATE,
                    status ENUM('tersedia', 'tugas', 'cuti', 'nonaktif') DEFAULT 'tersedia',
                    tarif_per_hari DECIMAL(10,2) DEFAULT 0,
                    rating DECIMAL(3,2) DEFAULT 5.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    -- Indexes
                    INDEX idx_nik (nik),
                    INDEX idx_status (status),
                    INDEX idx_nama (nama)
                ) ENGINE=InnoDB
            """,
            
            'driver_penyewaan': """
                CREATE TABLE IF NOT EXISTS driver_penyewaan (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    penyewaan_id INT NOT NULL,
                    driver_id INT NOT NULL,
                    tanggal_mulai DATETIME NOT NULL,
                    tanggal_selesai DATETIME NOT NULL,
                    total_hari INT NOT NULL,
                    total_biaya DECIMAL(10,2) NOT NULL,
                    status ENUM('aktif', 'selesai', 'batal') DEFAULT 'aktif',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    -- Foreign Keys
                    FOREIGN KEY (penyewaan_id) 
                        REFERENCES penyewaan(id) 
                        ON DELETE CASCADE 
                        ON UPDATE CASCADE,
                        
                    FOREIGN KEY (driver_id) 
                        REFERENCES driver(id) 
                        ON DELETE RESTRICT 
                        ON UPDATE CASCADE,
                    
                    -- Indexes
                    INDEX idx_penyewaan (penyewaan_id),
                    INDEX idx_driver (driver_id),
                    INDEX idx_status (status),
                    
                    -- Constraints
                    CHECK (total_hari > 0),
                    CHECK (total_biaya >= 0)
                ) ENGINE=InnoDB
            """,
            
            'maintenance': """
                CREATE TABLE IF NOT EXISTS maintenance (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    mobil_id INT NOT NULL,
                    tanggal_mulai DATE NOT NULL,
                    tanggal_selesai DATE,
                    jenis_maintenance ENUM('rutin', 'perbaikan', 'ganti_part') DEFAULT 'rutin',
                    deskripsi TEXT,
                    biaya DECIMAL(10,2) DEFAULT 0,
                    vendor VARCHAR(100),
                    status ENUM('dijadwalkan', 'diproses', 'selesai', 'batal') DEFAULT 'dijadwalkan',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    -- Foreign Key
                    FOREIGN KEY (mobil_id) 
                        REFERENCES mobil(id) 
                        ON DELETE CASCADE 
                        ON UPDATE CASCADE,
                    
                    -- Indexes
                    INDEX idx_mobil (mobil_id),
                    INDEX idx_status (status),
                    INDEX idx_tanggal (tanggal_mulai),
                    
                    -- Constraints
                    CHECK (biaya >= 0)
                ) ENGINE=InnoDB
            """,
            
            'audit_log': """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    tabel VARCHAR(50) NOT NULL,
                    id_record INT NOT NULL,
                    aksi ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
                    data_lama JSON,
                    data_baru JSON,
                    diubah_oleh VARCHAR(100),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Indexes
                    INDEX idx_tabel (tabel),
                    INDEX idx_waktu (waktu),
                    INDEX idx_aksi (aksi),
                    INDEX idx_id_record (id_record)
                ) ENGINE=InnoDB
            """
        }
        
        try:
            for table_name, create_query in table_queries.items():
                cursor.execute(create_query)
                self.print_success(f"Tabel '{table_name}' berhasil dibuat")
            
            self.connection.commit()
            self.print_success("Semua tabel berhasil dibuat!")
            return True
            
        except Error as e:
            self.print_error(f"Gagal membuat tabel: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def create_indexes(self):
        """Membuat additional indexes untuk optimasi"""
        cursor = self.connection.cursor()
        
        self.print_header("MEMBUAT ADDITIONAL INDEXES")
        
        try:
            # Additional indexes untuk query yang sering digunakan
            additional_indexes = [
                # Index untuk pencarian mobil
                "CREATE INDEX idx_mobil_search ON mobil (merk, model, tahun, harga_sewa_per_hari)",
                
                # Index untuk laporan berdasarkan tanggal sewa
                "CREATE INDEX idx_penyewaan_tanggal ON penyewaan (tanggal_sewa)",
                
                # Index untuk pelanggan berdasarkan kota
                "CREATE INDEX idx_pelanggan_kota ON pelanggan (kota, provinsi)",
                
                # Index untuk pembayaran berdasarkan status dan tanggal
                "CREATE INDEX idx_pembayaran_status_tanggal ON pembayaran (status, tanggal_bayar)",
                
                # Composite index untuk driver availability
                "CREATE INDEX idx_driver_availability ON driver (status, tarif_per_hari)",
            ]
            
            for i, index_query in enumerate(additional_indexes, 1):
                try:
                    cursor.execute(index_query)
                    self.print_success(f"Index {i} berhasil dibuat")
                except Error as e:
                    self.print_warning(f"Index {i} gagal (mungkin sudah ada): {e}")
            
            self.connection.commit()
            self.print_success("Additional indexes berhasil dibuat")
            return True
            
        except Error as e:
            self.print_error(f"Gagal membuat indexes: {e}")
            return False
        finally:
            cursor.close()
    
    def create_triggers(self):
        """Membuat triggers untuk maintain data integrity"""
        cursor = self.connection.cursor()
        
        self.print_header("MEMBUAT TRIGGERS")
        
        try:
            # Drop existing triggers jika ada
            cursor.execute("""
                SELECT TRIGGER_NAME 
                FROM INFORMATION_SCHEMA.TRIGGERS 
                WHERE TRIGGER_SCHEMA = %s
            """, (self.database_name,))
            
            existing_triggers = [row[0] for row in cursor.fetchall()]
            
            for trigger in existing_triggers:
                cursor.execute(f"DROP TRIGGER IF EXISTS {trigger}")
            
            # 1. Trigger: Update status mobil ketika disewa
            trigger_sewa_mobil = """
            CREATE TRIGGER trg_after_insert_penyewaan
            AFTER INSERT ON penyewaan
            FOR EACH ROW
            BEGIN
                DECLARE v_status VARCHAR(20);
                
                -- Hanya update jika status penyewaan bukan 'batal'
                IF NEW.status != 'batal' THEN
                    -- Cek apakah mobil masih tersedia
                    SELECT status INTO v_status 
                    FROM mobil 
                    WHERE id = NEW.mobil_id;
                    
                    IF v_status = 'tersedia' THEN
                        UPDATE mobil 
                        SET status = 'disewa',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = NEW.mobil_id;
                    ELSE
                        SIGNAL SQLSTATE '45000'
                        SET MESSAGE_TEXT = 'Mobil tidak tersedia untuk disewa';
                    END IF;
                END IF;
            END
            """
            
            # 2. Trigger: Update status mobil ketika pengembalian
            trigger_pengembalian_mobil = """
            CREATE TRIGGER trg_after_update_penyewaan
            AFTER UPDATE ON penyewaan
            FOR EACH ROW
            BEGIN
                -- Jika status berubah dari aktif ke selesai/terlambat
                IF OLD.status = 'aktif' AND NEW.status IN ('selesai', 'terlambat') THEN
                    UPDATE mobil 
                    SET status = 'tersedia',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = NEW.mobil_id;
                END IF;
                
                -- Jika penyewaan dibatalkan
                IF OLD.status != 'batal' AND NEW.status = 'batal' THEN
                    UPDATE mobil 
                    SET status = 'tersedia',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = NEW.mobil_id;
                END IF;
            END
            """
            
            # 3. Trigger: Update status mobil untuk maintenance
            trigger_maintenance_mobil = """
            CREATE TRIGGER trg_after_insert_maintenance
            AFTER INSERT ON maintenance
            FOR EACH ROW
            BEGIN
                IF NEW.status = 'diproses' THEN
                    UPDATE mobil 
                    SET status = 'perbaikan',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = NEW.mobil_id;
                END IF;
            END
            """
            
            # 4. Trigger: Update status mobil setelah maintenance selesai
            trigger_maintenance_selesai = """
            CREATE TRIGGER trg_after_update_maintenance
            AFTER UPDATE ON maintenance
            FOR EACH ROW
            BEGIN
                DECLARE v_disewa INT DEFAULT 0;
                
                IF OLD.status != 'selesai' AND NEW.status = 'selesai' THEN
                    -- Cek apakah mobil sedang disewa
                    SELECT COUNT(*) INTO v_disewa
                    FROM penyewaan
                    WHERE mobil_id = NEW.mobil_id 
                    AND status = 'aktif';
                    
                    IF v_disewa = 0 THEN
                        UPDATE mobil 
                        SET status = 'tersedia',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = NEW.mobil_id;
                    END IF;
                END IF;
            END
            """
            
            # 5. Trigger: Audit log untuk perubahan di tabel penyewaan
            trigger_audit_penyewaan = """
            CREATE TRIGGER trg_audit_penyewaan
            AFTER UPDATE ON penyewaan
            FOR EACH ROW
            BEGIN
                INSERT INTO audit_log (tabel, id_record, aksi, data_lama, data_baru)
                VALUES (
                    'penyewaan',
                    NEW.id,
                    'UPDATE',
                    JSON_OBJECT(
                        'status', OLD.status,
                        'denda', OLD.denda,
                        'total_biaya', OLD.total_biaya,
                        'tanggal_pengembalian', OLD.tanggal_pengembalian
                    ),
                    JSON_OBJECT(
                        'status', NEW.status,
                        'denda', NEW.denda,
                        'total_biaya', NEW.total_biaya,
                        'tanggal_pengembalian', NEW.tanggal_pengembalian
                    )
                );
            END
            """
            
            # 6. Trigger: Generate kode penyewaan otomatis
            trigger_kode_penyewaan = """
            CREATE TRIGGER trg_before_insert_penyewaan
            BEFORE INSERT ON penyewaan
            FOR EACH ROW
            BEGIN
                DECLARE next_id INT;
                DECLARE year_code VARCHAR(4);
                DECLARE month_code VARCHAR(2);
                
                -- Generate kode: RENT-YYYYMM-XXXX
                SET year_code = YEAR(CURRENT_DATE());
                SET month_code = LPAD(MONTH(CURRENT_DATE()), 2, '0');
                
                -- Cari ID berikutnya
                SELECT COALESCE(MAX(SUBSTRING(kode_penyewaan, 12)), 0) + 1 
                INTO next_id
                FROM penyewaan 
                WHERE kode_penyewaan LIKE CONCAT('RENT-', year_code, month_code, '-%');
                
                SET NEW.kode_penyewaan = CONCAT(
                    'RENT-', 
                    year_code, 
                    month_code, 
                    '-', 
                    LPAD(next_id, 4, '0')
                );
            END
            """
            
            # 7. Trigger: Generate kode pembayaran otomatis
            trigger_kode_pembayaran = """
            CREATE TRIGGER trg_before_insert_pembayaran
            BEFORE INSERT ON pembayaran
            FOR EACH ROW
            BEGIN
                DECLARE next_id INT;
                DECLARE year_code VARCHAR(4);
                DECLARE month_code VARCHAR(2);
                
                -- Generate kode: PAY-YYYYMM-XXXX
                SET year_code = YEAR(CURRENT_DATE());
                SET month_code = LPAD(MONTH(CURRENT_DATE()), 2, '0');
                
                -- Cari ID berikutnya
                SELECT COALESCE(MAX(SUBSTRING(kode_pembayaran, 11)), 0) + 1 
                INTO next_id
                FROM pembayaran 
                WHERE kode_pembayaran LIKE CONCAT('PAY-', year_code, month_code, '-%');
                
                SET NEW.kode_pembayaran = CONCAT(
                    'PAY-', 
                    year_code, 
                    month_code, 
                    '-', 
                    LPAD(next_id, 4, '0')
                );
            END
            """
            
            triggers = [
                # NOTE: Kode penyewaan dihasilkan di application level (service layer)
                # Trigger database menyebabkan conflict dengan sequence counter yang benar
                # ("Trigger kode penyewaan", trigger_kode_penyewaan),
                ("Trigger after insert penyewaan", trigger_sewa_mobil),
                ("Trigger after update penyewaan", trigger_pengembalian_mobil),
                ("Trigger audit penyewaan", trigger_audit_penyewaan),
                ("Trigger kode pembayaran", trigger_kode_pembayaran),
                ("Trigger maintenance mobil", trigger_maintenance_mobil),
                ("Trigger maintenance selesai", trigger_maintenance_selesai)
            ]
            
            for trigger_name, trigger_query in triggers:
                try:
                    cursor.execute(trigger_query)
                    self.print_success(trigger_name)
                except Error as e:
                    self.print_warning(f"{trigger_name} gagal: {e}")
            
            self.connection.commit()
            self.print_success("Semua triggers berhasil dibuat")
            return True
            
        except Error as e:
            self.print_error(f"Gagal membuat triggers: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def create_views(self):
        """Membuat views untuk reporting"""
        cursor = self.connection.cursor()
        
        self.print_header("MEMBUAT VIEWS UNTUK REPORTING")
        
        try:
            # 1. View: Mobil tersedia
            view_mobil_tersedia = """
            CREATE OR REPLACE VIEW view_mobil_tersedia AS
            SELECT 
                id, 
                merk, 
                model, 
                tahun, 
                warna,
                plat_nomor, 
                transmisi,
                bahan_bakar,
                kapasitas_penumpang,
                harga_sewa_per_hari,
                status,
                created_at
            FROM mobil 
            WHERE status = 'tersedia'
            ORDER BY merk, tahun DESC, harga_sewa_per_hari;
            """
            
            # 2. View: Penyewaan aktif dengan detail
            view_penyewaan_aktif = """
            CREATE OR REPLACE VIEW view_penyewaan_aktif AS
            SELECT 
                p.id,
                p.kode_penyewaan,
                p.tanggal_sewa,
                p.tanggal_kembali,
                p.total_biaya,
                p.denda,
                p.status,
                m.merk,
                m.model,
                m.plat_nomor,
                pl.nama as nama_pelanggan,
                pl.no_telepon as telp_pelanggan,
                pl.email as email_pelanggan,
                DATEDIFF(p.tanggal_kembali, CURDATE()) as hari_menuju_kembali
            FROM penyewaan p
            JOIN mobil m ON p.mobil_id = m.id
            JOIN pelanggan pl ON p.pelanggan_id = pl.id
            WHERE p.status IN ('aktif', 'terlambat')
            ORDER BY p.tanggal_kembali;
            """
            
            # 3. View: Laporan pendapatan bulanan
            view_pendapatan_bulanan = """
            CREATE OR REPLACE VIEW view_pendapatan_bulanan AS
            SELECT 
                YEAR(tanggal_sewa) as tahun,
                MONTH(tanggal_sewa) as bulan,
                DATE_FORMAT(tanggal_sewa, '%Y-%m') as periode,
                COUNT(*) as jumlah_transaksi,
                SUM(total_biaya) as total_biaya,
                SUM(denda) as total_denda,
                SUM(total_biaya + denda) as total_pendapatan,
                AVG(total_biaya) as rata_rata_transaksi
            FROM penyewaan
            WHERE status IN ('selesai', 'terlambat')
            GROUP BY YEAR(tanggal_sewa), MONTH(tanggal_sewa)
            ORDER BY tahun DESC, bulan DESC;
            """
            
            # 4. View: Statistik mobil
            view_statistik_mobil = """
            CREATE OR REPLACE VIEW view_statistik_mobil AS
            SELECT 
                m.id,
                m.merk,
                m.model,
                m.plat_nomor,
                m.status,
                COUNT(p.id) as total_penyewaan,
                COALESCE(SUM(p.total_biaya), 0) as total_pendapatan,
                COALESCE(AVG(p.total_biaya), 0) as rata_pendapatan,
                COALESCE(MAX(p.tanggal_sewa), m.created_at) as terakhir_disewa
            FROM mobil m
            LEFT JOIN penyewaan p ON m.id = p.mobil_id AND p.status IN ('selesai', 'terlambat')
            GROUP BY m.id
            ORDER BY total_pendapatan DESC;
            """
            
            # 5. View: Pelanggan aktif dengan statistik
            view_pelanggan_aktif = """
            CREATE OR REPLACE VIEW view_pelanggan_aktif AS
            SELECT 
                pl.id,
                pl.nik,
                pl.nama,
                pl.no_telepon,
                pl.email,
                pl.status_aktif,
                COUNT(p.id) as total_penyewaan,
                COALESCE(SUM(p.total_biaya + p.denda), 0) as total_pengeluaran,
                COALESCE(MAX(p.tanggal_sewa), pl.created_at) as terakhir_sewa,
                DATEDIFF(CURDATE(), COALESCE(MAX(p.tanggal_sewa), pl.created_at)) as hari_sejak_sewa_terakhir
            FROM pelanggan pl
            LEFT JOIN penyewaan p ON pl.id = p.pelanggan_id AND p.status IN ('selesai', 'terlambat')
            WHERE pl.status_aktif = 'aktif'
            GROUP BY pl.id
            ORDER BY total_pengeluaran DESC;
            """
            
            # 6. View: Driver tersedia
            view_driver_tersedia = """
            CREATE OR REPLACE VIEW view_driver_tersedia AS
            SELECT 
                id,
                nik,
                nama,
                no_telepon,
                sim_jenis,
                tarif_per_hari,
                rating,
                status
            FROM driver
            WHERE status = 'tersedia'
            ORDER BY rating DESC, tarif_per_hari;
            """
            
            # 7. View: Pembayaran pending
            view_pembayaran_pending = """
            CREATE OR REPLACE VIEW view_pembayaran_pending AS
            SELECT 
                pb.id,
                pb.kode_pembayaran,
                pb.jumlah,
                pb.metode_pembayaran,
                pb.status,
                pb.tanggal_bayar,
                p.kode_penyewaan,
                m.merk,
                m.model,
                pl.nama as pelanggan_nama
            FROM pembayaran pb
            JOIN penyewaan p ON pb.penyewaan_id = p.id
            JOIN mobil m ON p.mobil_id = m.id
            JOIN pelanggan pl ON p.pelanggan_id = pl.id
            WHERE pb.status IN ('pending', 'diproses')
            ORDER BY pb.tanggal_bayar;
            """
            
            views = [
                ("View mobil tersedia", view_mobil_tersedia),
                ("View penyewaan aktif", view_penyewaan_aktif),
                ("View pendapatan bulanan", view_pendapatan_bulanan),
                ("View statistik mobil", view_statistik_mobil),
                ("View pelanggan aktif", view_pelanggan_aktif),
                ("View driver tersedia", view_driver_tersedia),
                ("View pembayaran pending", view_pembayaran_pending)
            ]
            
            for view_name, view_query in views:
                try:
                    cursor.execute(view_query)
                    self.print_success(view_name)
                except Error as e:
                    self.print_warning(f"{view_name} gagal: {e}")
            
            self.connection.commit()
            self.print_success("Semua views berhasil dibuat")
            return True
            
        except Error as e:
            self.print_error(f"Gagal membuat views: {e}")
            return False
        finally:
            cursor.close()
    
    def create_stored_procedures(self):
        """Membuat stored procedures untuk operasi umum"""
        cursor = self.connection.cursor()
        
        self.print_header("MEMBUAT STORED PROCEDURES")
        
        try:
            # Drop existing procedures
            cursor.execute("""
                SELECT ROUTINE_NAME 
                FROM INFORMATION_SCHEMA.ROUTINES 
                WHERE ROUTINE_SCHEMA = %s AND ROUTINE_TYPE = 'PROCEDURE'
            """, (self.database_name,))
            
            existing_procedures = [row[0] for row in cursor.fetchall()]
            
            for procedure in existing_procedures:
                cursor.execute(f"DROP PROCEDURE IF EXISTS {procedure}")
            
            # 1. Procedure: Sewa mobil
            proc_sewa_mobil = """
            CREATE PROCEDURE sp_sewa_mobil(
                IN p_mobil_id INT,
                IN p_pelanggan_id INT,
                IN p_tanggal_sewa DATETIME,
                IN p_jumlah_hari INT,
                IN p_lokasi_penjemputan VARCHAR(255),
                IN p_catatan TEXT,
                OUT p_penyewaan_id INT,
                OUT p_kode_penyewaan VARCHAR(20),
                OUT p_total_biaya DECIMAL(12,2),
                OUT p_message VARCHAR(255)
            )
            BEGIN
                DECLARE v_harga_per_hari DECIMAL(10,2);
                DECLARE v_status_mobil VARCHAR(20);
                DECLARE v_tanggal_kembali DATETIME;
                DECLARE v_status_pelanggan VARCHAR(20);
                
                -- Cek status pelanggan
                SELECT status_aktif INTO v_status_pelanggan
                FROM pelanggan 
                WHERE id = p_pelanggan_id;
                
                IF v_status_pelanggan IS NULL THEN
                    SET p_message = 'Pelanggan tidak ditemukan';
                    SET p_penyewaan_id = NULL;
                    SET p_kode_penyewaan = NULL;
                    SET p_total_biaya = 0;
                ELSEIF v_status_pelanggan != 'aktif' THEN
                    SET p_message = CONCAT('Pelanggan status: ', v_status_pelanggan);
                    SET p_penyewaan_id = NULL;
                    SET p_kode_penyewaan = NULL;
                    SET p_total_biaya = 0;
                ELSE
                    -- Cek ketersediaan mobil
                    SELECT harga_sewa_per_hari, status 
                    INTO v_harga_per_hari, v_status_mobil
                    FROM mobil 
                    WHERE id = p_mobil_id;
                    
                    IF v_status_mobil IS NULL THEN
                        SET p_message = 'Mobil tidak ditemukan';
                        SET p_penyewaan_id = NULL;
                        SET p_kode_penyewaan = NULL;
                        SET p_total_biaya = 0;
                    ELSEIF v_status_mobil != 'tersedia' THEN
                        SET p_message = CONCAT('Mobil sedang ', v_status_mobil);
                        SET p_penyewaan_id = NULL;
                        SET p_kode_penyewaan = NULL;
                        SET p_total_biaya = 0;
                    ELSE
                        -- Hitung biaya
                        SET p_total_biaya = v_harga_per_hari * p_jumlah_hari;
                        SET v_tanggal_kembali = DATE_ADD(p_tanggal_sewa, INTERVAL p_jumlah_hari DAY);
                        
                        -- Insert penyewaan (kode akan di-generate oleh trigger)
                        INSERT INTO penyewaan (
                            mobil_id, 
                            pelanggan_id, 
                            tanggal_sewa, 
                            tanggal_kembali,
                            total_hari, 
                            total_biaya,
                            lokasi_penjemputan,
                            catatan,
                            status
                        ) VALUES (
                            p_mobil_id, 
                            p_pelanggan_id, 
                            p_tanggal_sewa,
                            v_tanggal_kembali, 
                            p_jumlah_hari, 
                            p_total_biaya,
                            p_lokasi_penjemputan,
                            p_catatan,
                            'pending'
                        );
                        
                        SET p_penyewaan_id = LAST_INSERT_ID();
                        
                        -- Ambil kode penyewaan yang di-generate
                        SELECT kode_penyewaan INTO p_kode_penyewaan
                        FROM penyewaan 
                        WHERE id = p_penyewaan_id;
                        
                        SET p_message = CONCAT(
                            'Penyewaan berhasil dibuat. ',
                            'Kode: ', p_kode_penyewaan, '. ',
                            'Total biaya: Rp ', FORMAT(p_total_biaya, 0)
                        );
                    END IF;
                END IF;
            END
            """
            
            # 2. Procedure: Pengembalian mobil
            proc_pengembalian_mobil = """
            CREATE PROCEDURE sp_pengembalian_mobil(
                IN p_penyewaan_id INT,
                IN p_tanggal_pengembalian DATETIME,
                IN p_kondisi_mobil ENUM('baik', 'rusak_ringan', 'rusak_berat'),
                IN p_catatan_kerusakan TEXT,
                IN p_biaya_tambahan DECIMAL(10,2),
                IN p_km_akhir INT,
                IN p_dikembalikan_oleh VARCHAR(100),
                OUT p_denda DECIMAL(10,2),
                OUT p_total_bayar DECIMAL(12,2),
                OUT p_message VARCHAR(255)
            )
            BEGIN
                DECLARE v_harga_per_hari DECIMAL(10,2);
                DECLARE v_tanggal_kembali DATETIME;
                DECLARE v_total_biaya DECIMAL(12,2);
                DECLARE v_status VARCHAR(20);
                DECLARE v_mobil_id INT;
                DECLARE v_hari_keterlambatan INT;
                DECLARE v_biaya_tambahan_final DECIMAL(10,2) DEFAULT 0;
                
                -- Get rental details
                SELECT 
                    m.harga_sewa_per_hari,
                    p.tanggal_kembali,
                    p.total_biaya,
                    p.status,
                    p.mobil_id
                INTO 
                    v_harga_per_hari,
                    v_tanggal_kembali,
                    v_total_biaya,
                    v_status,
                    v_mobil_id
                FROM penyewaan p
                JOIN mobil m ON p.mobil_id = m.id
                WHERE p.id = p_penyewaan_id;
                
                IF v_status IS NULL THEN
                    SET p_message = 'Penyewaan tidak ditemukan';
                    SET p_denda = 0;
                    SET p_total_bayar = 0;
                ELSEIF v_status != 'aktif' THEN
                    SET p_message = CONCAT('Penyewaan sudah ', v_status);
                    SET p_denda = 0;
                    SET p_total_bayar = 0;
                ELSE
                    -- Hitung keterlambatan
                    SET v_hari_keterlambatan = GREATEST(0, TIMESTAMPDIFF(HOUR, v_tanggal_kembali, p_tanggal_pengembalian) / 24);
                    
                    -- Hitung denda (10% per jam keterlambatan, maksimal 150% per hari)
                    SET p_denda = v_harga_per_hari * LEAST(v_hari_keterlambatan * 1.5, 3.0);
                    
                    -- Hitung biaya tambahan untuk kerusakan
                    IF p_kondisi_mobil = 'rusak_ringan' THEN
                        SET v_biaya_tambahan_final = v_harga_per_hari * 0.5;
                    ELSEIF p_kondisi_mobil = 'rusak_berat' THEN
                        SET v_biaya_tambahan_final = v_harga_per_hari * 2;
                    END IF;
                    
                    -- Tambahkan biaya tambahan dari input
                    SET v_biaya_tambahan_final = v_biaya_tambahan_final + COALESCE(p_biaya_tambahan, 0);
                    
                    -- Update penyewaan
                    UPDATE penyewaan 
                    SET 
                        tanggal_pengembalian = p_tanggal_pengembalian,
                        denda = p_denda,
                        status = CASE 
                            WHEN v_hari_keterlambatan > 0 THEN 'terlambat'
                            ELSE 'selesai'
                        END,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = p_penyewaan_id;
                    
                    -- Insert ke tabel pengembalian
                    INSERT INTO pengembalian (
                        penyewaan_id,
                        tanggal_pengembalian,
                        kondisi_mobil,
                        catatan_kerusakan,
                        biaya_tambahan,
                        km_akhir,
                        dikembalikan_oleh,
                        diterima_oleh
                    ) VALUES (
                        p_penyewaan_id,
                        p_tanggal_pengembalian,
                        p_kondisi_mobil,
                        p_catatan_kerusakan,
                        v_biaya_tambahan_final,
                        p_km_akhir,
                        p_dikembalikan_oleh,
                        CURRENT_USER()
                    );
                    
                    -- Hitung total yang harus dibayar
                    SET p_total_bayar = v_total_biaya + p_denda + v_biaya_tambahan_final;
                    
                    SET p_message = CONCAT(
                        'Pengembalian berhasil. ',
                        CASE 
                            WHEN v_hari_keterlambatan > 0 
                            THEN CONCAT('Keterlambatan: ', ROUND(v_hari_keterlambatan, 1), ' hari. ')
                            ELSE ''
                        END,
                        CASE 
                            WHEN v_biaya_tambahan_final > 0
                            THEN CONCAT('Biaya kerusakan: Rp ', FORMAT(v_biaya_tambahan_final, 0), '. ')
                            ELSE ''
                        END,
                        'Total yang harus dibayar: Rp ', FORMAT(p_total_bayar, 0)
                    );
                END IF;
            END
            """
            
            # 3. Procedure: Laporan harian
            proc_laporan_harian = """
            CREATE PROCEDURE sp_laporan_harian(
                IN p_tanggal DATE,
                OUT p_total_transaksi INT,
                OUT p_total_pendapatan DECIMAL(12,2),
                OUT p_total_denda DECIMAL(10,2),
                OUT p_jumlah_mobil_tersedia INT
            )
            BEGIN
                -- Total transaksi pada tanggal tertentu
                SELECT COUNT(*) INTO p_total_transaksi
                FROM penyewaan
                WHERE DATE(tanggal_sewa) = p_tanggal;
                
                -- Total pendapatan
                SELECT COALESCE(SUM(total_biaya + denda), 0) INTO p_total_pendapatan
                FROM penyewaan
                WHERE DATE(tanggal_sewa) = p_tanggal
                AND status IN ('selesai', 'terlambat');
                
                -- Total denda
                SELECT COALESCE(SUM(denda), 0) INTO p_total_denda
                FROM penyewaan
                WHERE DATE(tanggal_sewa) = p_tanggal;
                
                -- Jumlah mobil tersedia
                SELECT COUNT(*) INTO p_jumlah_mobil_tersedia
                FROM mobil
                WHERE status = 'tersedia';
            END
            """
            
            # 4. Procedure: Cari mobil tersedia
            proc_cari_mobil_tersedia = """
            CREATE PROCEDURE sp_cari_mobil_tersedia(
                IN p_merk VARCHAR(100),
                IN p_tahun_min INT,
                IN p_tahun_max INT,
                IN p_harga_max DECIMAL(10,2),
                IN p_transmisi VARCHAR(20),
                IN p_bahan_bakar VARCHAR(20),
                IN p_kapasitas_min INT
            )
            BEGIN
                SELECT 
                    id,
                    merk,
                    model,
                    tahun,
                    warna,
                    plat_nomor,
                    transmisi,
                    bahan_bakar,
                    kapasitas_penumpang,
                    harga_sewa_per_hari,
                    status,
                    deskripsi
                FROM mobil
                WHERE status = 'tersedia'
                AND (p_merk IS NULL OR merk LIKE CONCAT('%', p_merk, '%'))
                AND (p_tahun_min IS NULL OR tahun >= p_tahun_min)
                AND (p_tahun_max IS NULL OR tahun <= p_tahun_max)
                AND (p_harga_max IS NULL OR harga_sewa_per_hari <= p_harga_max)
                AND (p_transmisi IS NULL OR transmisi = p_transmisi)
                AND (p_bahan_bakar IS NULL OR bahan_bakar = p_bahan_bakar)
                AND (p_kapasitas_min IS NULL OR kapasitas_penumpang >= p_kapasitas_min)
                ORDER BY harga_sewa_per_hari, tahun DESC;
            END
            """
            
            # 5. Procedure: Update status pembayaran
            proc_update_status_pembayaran = """
            CREATE PROCEDURE sp_update_status_pembayaran(
                IN p_pembayaran_id INT,
                IN p_status ENUM('pending', 'diproses', 'lunas', 'gagal', 'dibatalkan', 'refund'),
                IN p_keterangan TEXT,
                IN p_bukti_pembayaran TEXT,
                OUT p_message VARCHAR(255)
            )
            BEGIN
                DECLARE v_penyewaan_id INT;
                DECLARE v_status_sebelum VARCHAR(20);
                
                -- Get current status and penyewaan_id
                SELECT status, penyewaan_id 
                INTO v_status_sebelum, v_penyewaan_id
                FROM pembayaran 
                WHERE id = p_pembayaran_id;
                
                IF v_status_sebelum IS NULL THEN
                    SET p_message = 'Pembayaran tidak ditemukan';
                ELSE
                    -- Update pembayaran
                    UPDATE pembayaran 
                    SET 
                        status = p_status,
                        keterangan = p_keterangan,
                        bukti_pembayaran = COALESCE(p_bukti_pembayaran, bukti_pembayaran),
                        tanggal_konfirmasi = CASE 
                            WHEN p_status = 'lunas' THEN CURRENT_TIMESTAMP
                            ELSE tanggal_konfirmasi
                        END,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = p_pembayaran_id;
                    
                    -- Jika status menjadi lunas, update status penyewaan
                    IF p_status = 'lunas' AND v_status_sebelum != 'lunas' THEN
                        UPDATE penyewaan
                        SET status = 'aktif',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = v_penyewaan_id;
                    END IF;
                    
                    SET p_message = CONCAT(
                        'Status pembayaran berhasil diubah dari ',
                        v_status_sebelum,
                        ' menjadi ',
                        p_status
                    );
                END IF;
            END
            """
            
            procedures = [
                ("Procedure sewa mobil", proc_sewa_mobil),
                ("Procedure pengembalian mobil", proc_pengembalian_mobil),
                ("Procedure laporan harian", proc_laporan_harian),
                ("Procedure cari mobil tersedia", proc_cari_mobil_tersedia),
                ("Procedure update status pembayaran", proc_update_status_pembayaran)
            ]
            
            for proc_name, proc_query in procedures:
                try:
                    cursor.execute(proc_query)
                    self.print_success(proc_name)
                except Error as e:
                    self.print_warning(f"{proc_name} gagal: {e}")
            
            self.connection.commit()
            self.print_success("Stored procedures berhasil dibuat")
            return True
            
        except Error as e:
            self.print_error(f"Gagal membuat stored procedures: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def insert_sample_data(self):
        """Memasukkan data contoh untuk testing"""
        cursor = self.connection.cursor()
        
        self.print_header("MEMASUKKAN DATA CONTOH")
        
        try:
            # 1. Insert data MOBIL (15 mobil)
            mobil_data = [
                # Toyota
                ('Toyota', 'Avanza', 2022, 'B 1234 ABC', 'Putih', 'manual', 'bensin', 7, 300000, 'tersedia', 'Mobil keluarga dengan kondisi prima'),
                ('Toyota', 'Fortuner', 2023, 'B 2345 BCD', 'Hitam', 'automatic', 'solar', 7, 600000, 'tersedia', 'SUV mewah dengan fitur lengkap'),
                ('Toyota', 'Innova', 2021, 'B 3456 CDE', 'Silver', 'automatic', 'bensin', 8, 450000, 'tersedia', 'Mobil baru servis berkala'),
                ('Toyota', 'Rush', 2022, 'B 4567 DEF', 'Merah', 'manual', 'bensin', 5, 350000, 'tersedia', 'Compact SUV'),
                ('Toyota', 'Yaris', 2023, 'B 5678 EFG', 'Biru', 'automatic', 'bensin', 5, 400000, 'tersedia', 'Hatchback sporty'),
                
                # Honda
                ('Honda', 'Brio', 2021, 'B 6789 FGH', 'Kuning', 'manual', 'bensin', 5, 250000, 'tersedia', 'City car ekonomis'),
                ('Honda', 'HR-V', 2023, 'B 7890 GHI', 'Putih', 'automatic', 'bensin', 5, 500000, 'tersedia', 'Sedang maintenance'),
                ('Honda', 'CR-V', 2022, 'B 8901 HIJ', 'Hitam', 'automatic', 'bensin', 5, 550000, 'tersedia', 'SUV premium'),
                ('Honda', 'Civic', 2023, 'B 9012 IJK', 'Abu-abu', 'automatic', 'bensin', 5, 650000, 'tersedia', 'Sedan mewah'),
                
                # Mitsubishi
                ('Mitsubishi', 'Xpander', 2023, 'B 1122 JKL', 'Putih', 'automatic', 'bensin', 7, 400000, 'tersedia', 'MPV terlaris'),
                ('Mitsubishi', 'Pajero', 2022, 'B 2233 KLM', 'Hitam', 'automatic', 'solar', 7, 700000, 'tersedia', 'SUV tangguh'),
                
                # Suzuki
                ('Suzuki', 'Ertiga', 2020, 'B 3344 LMN', 'Merah', 'manual', 'bensin', 7, 280000, 'tersedia', 'MPV keluarga'),
                ('Suzuki', 'XL7', 2023, 'B 4455 MNO', 'Putih', 'automatic', 'bensin', 7, 380000, 'tersedia', 'MPV modern'),
                
                # Daihatsu
                ('Daihatsu', 'Sigra', 2021, 'B 5566 NOP', 'Silver', 'manual', 'bensin', 7, 275000, 'tersedia', 'LCGC irit'),
                
                # Wuling
                ('Wuling', 'Cortez', 2023, 'B 6677 OPQ', 'Biru', 'automatic', 'bensin', 7, 350000, 'tersedia', 'MPV elegan'),
            ]
            
            insert_mobil = """
            INSERT INTO mobil 
            (merk, model, tahun, plat_nomor, warna, transmisi, bahan_bakar, 
             kapasitas_penumpang, harga_sewa_per_hari, status, deskripsi) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_mobil, mobil_data)
            self.print_success(f"{cursor.rowcount} data mobil berhasil dimasukkan")
            
            # 2. Insert data PELANGGAN (10 pelanggan)
            pelanggan_data = [
                ('1234567890123456', 'Budi Santoso', 'L', '1990-05-15', 'Jl. Merdeka No. 1', 'Jakarta', 'DKI Jakarta', '10110', '081234567890', 'budi.santoso@email.com', 'Karyawan Swasta', 'aktif'),
                ('2345678901234567', 'Siti Rahayu', 'P', '1985-08-20', 'Jl. Sudirman No. 45', 'Bandung', 'Jawa Barat', '40115', '082345678901', 'siti.rahayu@email.com', 'PNS', 'aktif'),
                ('3456789012345678', 'Ahmad Wijaya', 'L', '1992-03-10', 'Jl. Thamrin No. 12', 'Surabaya', 'Jawa Timur', '60111', '083456789012', 'ahmad.wijaya@email.com', 'Wiraswasta', 'aktif'),
                ('4567890123456789', 'Dewi Lestari', 'P', '1988-11-25', 'Jl. Gatot Subroto No. 23', 'Medan', 'Sumatera Utara', '20112', '084567890123', 'dewi.lestari@email.com', 'Dokter', 'aktif'),
                ('5678901234567890', 'Rudi Hartono', 'L', '1995-07-30', 'Jl. Pemuda No. 56', 'Semarang', 'Jawa Tengah', '50111', '085678901234', 'rudi.hartono@email.com', 'Mahasiswa', 'aktif'),
                ('6789012345678901', 'Maya Sari', 'P', '1993-02-14', 'Jl. Asia Afrika No. 78', 'Bogor', 'Jawa Barat', '16111', '086789012345', 'maya.sari@email.com', 'Guru', 'aktif'),
                ('7890123456789012', 'Fajar Nugroho', 'L', '1987-09-05', 'Jl. Pahlawan No. 34', 'Malang', 'Jawa Timur', '65111', '087890123456', 'fajar.nugroho@email.com', 'Pengusaha', 'aktif'),
                ('8901234567890123', 'Linda Wati', 'P', '1991-12-12', 'Jl. Diponegoro No. 67', 'Denpasar', 'Bali', '80222', '088901234567', 'linda.wati@email.com', 'Akuntan', 'aktif'),
                ('9012345678901234', 'Joko Susilo', 'L', '1994-04-18', 'Jl. Ahmad Yani No. 89', 'Yogyakarta', 'DIY', '55211', '089012345678', 'joko.susilo@email.com', 'Programmer', 'aktif'),
                ('0123456789012345', 'Ratna Dewi', 'P', '1989-06-22', 'Jl. Urip Sumoharjo No. 11', 'Makassar', 'Sulawesi Selatan', '90111', '081112233445', 'ratna.dewi@email.com', 'Arsitek', 'nonaktif'),
            ]
            
            insert_pelanggan = """
            INSERT INTO pelanggan 
            (nik, nama, jenis_kelamin, tanggal_lahir, alamat, kota, provinsi, kode_pos, 
             no_telepon, email, pekerjaan, status_aktif) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_pelanggan, pelanggan_data)
            self.print_success(f"{cursor.rowcount} data pelanggan berhasil dimasukkan")
            
            # 3. Insert data DRIVER (5 driver)
            driver_data = [
                ('1122334455667788', 'Asep Sunarya', '081223344556', 'Jl. Cempaka No. 5, Bandung', '1980-01-15', '1234567890', 'A', '2025-12-31', 'tersedia', 150000, 4.5),
                ('2233445566778899', 'Dede Hermawan', '082334455667', 'Jl. Mawar No. 12, Jakarta', '1985-03-20', '2345678901', 'B1', '2024-11-30', 'tersedia', 120000, 4.2),
                ('3344556677889900', 'Jajang Nurjaman', '083445566778', 'Jl. Melati No. 8, Surabaya', '1978-07-10', '3456789012', 'B2', '2025-06-30', 'tugas', 130000, 4.0),
                ('4455667788990011', 'Ujang Saepudin', '084556677889', 'Jl. Anggrek No. 3, Bandung', '1990-11-05', '4567890123', 'C', '2024-09-30', 'tersedia', 100000, 3.8),
                ('5566778899001122', 'Maman Suherman', '085667788990', 'Jl. Kenanga No. 7, Jakarta', '1982-05-25', '5678901234', 'A', '2025-03-31', 'cuti', 140000, 4.7),
            ]
            
            insert_driver = """
            INSERT INTO driver 
            (nik, nama, no_telepon, alamat, tanggal_lahir, sim_nomor, sim_jenis, sim_expiry, status, tarif_per_hari, rating) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_driver, driver_data)
            self.print_success(f"{cursor.rowcount} data driver berhasil dimasukkan")
            
            # 4. Insert data PENYEWAAN (contoh transaksi)
            # Ambil ID mobil dan pelanggan yang sudah ada
            cursor.execute("SELECT id FROM mobil WHERE plat_nomor = 'B 4567 DEF'")  # Toyota Rush
            mobil_id_1 = cursor.fetchone()[0]
            
            cursor.execute("SELECT id FROM mobil WHERE plat_nomor = 'B 7890 GHI'")  # Honda HR-V (perbaikan)
            mobil_id_2 = cursor.fetchone()[0]
            
            cursor.execute("SELECT id FROM pelanggan WHERE nik = '1234567890123456'")  # Budi Santoso
            pelanggan_id_1 = cursor.fetchone()[0]
            
            cursor.execute("SELECT id FROM pelanggan WHERE nik = '2345678901234567'")  # Siti Rahayu
            pelanggan_id_2 = cursor.fetchone()[0]
            
            # Generate tanggal
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            last_week = today - timedelta(days=7)
            next_week = today + timedelta(days=7)
            
            # Data penyewaan (akan di-generate kode-nya oleh trigger)
            # Insert dengan status 'pending' terlebih dahulu untuk menghindari konflik trigger
            penyewaan_data = [
                # Penyewaan pending (Toyota Rush)
                (mobil_id_1, pelanggan_id_1, yesterday, next_week, 'Hotel Grand Indonesia, Jakarta', 8, 2800000, 0, 'pending', 'Untuk keperluan keluarga liburan'),
                
                # Penyewaan completed (Honda HR-V)
                (mobil_id_2, pelanggan_id_2, last_week, last_week + timedelta(days=3), 'Bandara Soekarno-Hatta', 3, 1050000, 0, 'selesai', 'Untuk meeting di Bandung'),
            ]
            
            insert_penyewaan = """
            INSERT INTO penyewaan 
            (mobil_id, pelanggan_id, tanggal_sewa, tanggal_kembali, lokasi_penjemputan, 
             total_hari, total_biaya, denda, status, catatan) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_penyewaan, penyewaan_data)
            self.print_success(f"{cursor.rowcount} data penyewaan berhasil dimasukkan")
            
            # 5. Insert data PEMBAYARAN
            cursor.execute("SELECT id FROM penyewaan LIMIT 2")
            penyewaan_ids = [row[0] for row in cursor.fetchall()]
            
            pembayaran_data = [
                (penyewaan_ids[0], 2800000, 'transfer', 'lunas', today - timedelta(days=1), None, 'BCA', '1234567890', 'Budi Santoso', 'bukti_transfer_001.jpg', 'Lunas via transfer BCA'),
                (penyewaan_ids[1], 1800000, 'kartu_kredit', 'lunas', last_week + timedelta(days=1), last_week + timedelta(days=2), 'Mandiri', None, None, 'bukti_cc_002.jpg', 'Termasuk denda keterlambatan'),
            ]
            
            insert_pembayaran = """
            INSERT INTO pembayaran 
            (penyewaan_id, jumlah, metode_pembayaran, status, tanggal_bayar, tanggal_konfirmasi,
             bank_tujuan, no_rekening, nama_rekening, bukti_pembayaran, keterangan) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_pembayaran, pembayaran_data)
            self.print_success(f"{cursor.rowcount} data pembayaran berhasil dimasukkan")
            
            # 6. Insert data PENGEMBALIAN untuk penyewaan yang selesai
            cursor.execute("SELECT id FROM penyewaan WHERE status = 'selesai'")
            penyewaan_selesai_id = cursor.fetchone()[0]
            
            insert_pengembalian = """
            INSERT INTO pengembalian 
            (penyewaan_id, tanggal_pengembalian, kondisi_mobil, catatan_kerusakan, 
             biaya_tambahan, km_akhir, km_awal, dikembalikan_oleh, diterima_oleh) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_pengembalian, (
                penyewaan_selesai_id,
                last_week + timedelta(days=4),  # Telat 1 hari
                'rusak_ringan',
                'Goresan kecil di pintu kanan depan',
                250000,  # Biaya kerusakan
                12500,
                12000,
                'Siti Rahayu',
                'Staff Rental'
            ))
            self.print_success("Data pengembalian berhasil dimasukkan")
            
            # 7. Insert data MAINTENANCE
            cursor.execute("SELECT id FROM mobil WHERE status = 'perbaikan'")
            mobil_perbaikan_result = cursor.fetchone()
            
            if mobil_perbaikan_result:
                mobil_perbaikan_id = mobil_perbaikan_result[0]
                insert_maintenance = """
                INSERT INTO maintenance 
                (mobil_id, tanggal_mulai, tanggal_selesai, jenis_maintenance, 
                 deskripsi, biaya, vendor, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_maintenance, (
                    mobil_perbaikan_id,
                    today - timedelta(days=2),
                    today + timedelta(days=3),
                    'perbaikan',
                    'Ganti shockbreaker dan servis berkala',
                    1200000,
                    'Bengkel Resmi Honda',
                    'diproses'
                ))
                self.print_success("Data maintenance berhasil dimasukkan")
            else:
                self.print_info("Tidak ada mobil dengan status perbaikan untuk maintenance")
            
            # 8. Insert data DRIVER_PENYEWAAN
            cursor.execute("SELECT id FROM driver WHERE status = 'tugas' LIMIT 1")
            driver_tugas_result = cursor.fetchone()
            
            cursor.execute("SELECT id FROM penyewaan WHERE status = 'pending'")
            penyewaan_pending_result = cursor.fetchone()
            
            if driver_tugas_result and penyewaan_pending_result:
                driver_tugas_id = driver_tugas_result[0]
                penyewaan_pending_id = penyewaan_pending_result[0]
                
                insert_driver_penyewaan = """
                INSERT INTO driver_penyewaan 
                (penyewaan_id, driver_id, tanggal_mulai, tanggal_selesai, 
                 total_hari, total_biaya, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_driver_penyewaan, (
                    penyewaan_pending_id,
                    driver_tugas_id,
                    yesterday,
                    next_week,
                    8,
                    960000,  # 8 hari * 120000/hari
                    'aktif'
                ))
                self.print_success("Data driver penyewaan berhasil dimasukkan")
            else:
                self.print_info("Tidak ada driver atau penyewaan untuk driver_penyewaan")
            
            self.connection.commit()
            
            # Tampilkan summary
            self.show_database_summary()
            
            return True
            
        except Error as e:
            self.print_error(f"Gagal memasukkan data contoh: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def show_database_summary(self):
        """Menampilkan summary database"""
        cursor = self.connection.cursor(dictionary=True)
        
        self.print_header("SUMMARY DATABASE RENTAL MOBIL")
        
        try:
            print("\n📊 STATISTIK UMUM:")
            print("-" * 40)
            
            # Hitung jumlah data di setiap tabel
            tables = ['mobil', 'pelanggan', 'penyewaan', 'pembayaran', 'pengembalian', 'driver', 'driver_penyewaan', 'maintenance', 'audit_log']
            
            table_stats = []
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                result = cursor.fetchone()
                table_stats.append([table.capitalize(), result['count']])
            
            # Tampilkan tabel stats
            for stat in table_stats:
                print(f"{stat[0]:20}: {stat[1]:>5} records")
            
            # Status mobil
            print("\n🚗 STATUS MOBIL:")
            print("-" * 40)
            cursor.execute("""
                SELECT status, COUNT(*) as jumlah 
                FROM mobil 
                GROUP BY status 
                ORDER BY status
            """)
            for row in cursor.fetchall():
                print(f"  {row['status']:15}: {row['jumlah']:>3} unit")
            
            # Status penyewaan
            print("\n📋 STATUS PENYEWAAN:")
            print("-" * 40)
            cursor.execute("""
                SELECT status, COUNT(*) as jumlah 
                FROM penyewaan 
                GROUP BY status 
                ORDER BY FIELD(status, 'aktif', 'pending', 'selesai', 'terlambat', 'batal')
            """)
            for row in cursor.fetchall():
                print(f"  {row['status']:15}: {row['jumlah']:>3} transaksi")
            
            # Total pendapatan
            print("\n💰 PENDAPATAN:")
            print("-" * 40)
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(total_biaya), 0) as total_biaya,
                    COALESCE(SUM(denda), 0) as total_denda,
                    COALESCE(SUM(total_biaya + denda), 0) as total_pendapatan
                FROM penyewaan 
                WHERE status IN ('selesai', 'terlambat')
            """)
            pendapatan = cursor.fetchone()
            
            print(f"  Biaya Sewa  : Rp {pendapatan['total_biaya']:>15,.0f}")
            print(f"  Denda       : Rp {pendapatan['total_denda']:>15,.0f}")
            print(f"  Total       : Rp {pendapatan['total_pendapatan']:>15,.0f}")
            
            # Top 3 mobil paling sering disewa
            print("\n🏆 TOP 3 MOBIL POPULER:")
            print("-" * 40)
            cursor.execute("""
                SELECT 
                    m.merk,
                    m.model,
                    m.plat_nomor,
                    COUNT(p.id) as jumlah_penyewaan,
                    COALESCE(SUM(p.total_biaya), 0) as total_pendapatan
                FROM mobil m
                LEFT JOIN penyewaan p ON m.id = p.mobil_id
                GROUP BY m.id
                ORDER BY jumlah_penyewaan DESC, total_pendapatan DESC
                LIMIT 3
            """)
            
            top_mobils = cursor.fetchall()
            for i, mobil in enumerate(top_mobils, 1):
                print(f"  {i}. {mobil['merk']} {mobil['model']} ({mobil['plat_nomor']})")
                print(f"     Disewa: {mobil['jumlah_penyewaan']} kali")
                print(f"     Pendapatan: Rp {mobil['total_pendapatan']:,.0f}")
            
            # Database info
            print("\nℹ️ DATABASE INFO:")
            print("-" * 40)
            cursor.execute("SELECT DATABASE() as db_name, USER() as db_user, @@hostname as hostname")
            db_info = cursor.fetchone()
            print(f"  Database    : {db_info['db_name']}")
            print(f"  User        : {db_info['db_user']}")
            print(f"  Host        : {db_info['hostname']}")
            
            # Cek trigger dan procedures
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TRIGGERS WHERE TRIGGER_SCHEMA = DATABASE()) as trigger_count,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE') as procedure_count,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = DATABASE()) as view_count
            """)
            feature_counts = cursor.fetchone()
            
            print(f"\n⚙️ FITUR DATABASE:")
            print("-" * 40)
            print(f"  Triggers    : {feature_counts['trigger_count']}")
            print(f"  Procedures  : {feature_counts['procedure_count']}")
            print(f"  Views       : {feature_counts['view_count']}")
            
        except Error as e:
            self.print_error(f"Error showing summary: {e}")
        finally:
            cursor.close()
    
    def run_all_setup(self):
        """Menjalankan semua proses setup"""
        self.print_header("SETUP DATABASE RENTAL MOBIL")
        print(f"{self.COLORS['BOLD']}Host: {self.host} | User: {self.user} | Database: {self.database_name}{self.COLORS['ENDC']}")
        print("\nProses akan menjalankan:")
        print("1. ✅ Koneksi ke MySQL server")
        print("2. ✅ Membuat database")
        print("3. ✅ Membuat tabel-tabel")
        print("4. ✅ Membuat indexes")
        print("5. ✅ Membuat triggers")
        print("6. ✅ Membuat views")
        print("7. ✅ Membuat stored procedures")
        print("8. ✅ Memasukkan data contoh")
        
        confirm = input(f"\n{self.COLORS['WARNING']}Lanjutkan setup? (y/n): {self.COLORS['ENDC']}").strip().lower()
        
        if confirm != 'y':
            self.print_info("Setup dibatalkan")
            return False
        
        steps = [
            ("Membuat koneksi", self.connect_without_db),
            ("Membuat database", self.create_database),
            ("Membuat tabel", self.create_tables),
            ("Membuat indexes", self.create_indexes),
            ("Membuat triggers", self.create_triggers),
            ("Membuat views", self.create_views),
            ("Membuat stored procedures", self.create_stored_procedures),
        ]
        
        # Jalankan semua steps
        for step_name, step_func in steps:
            print(f"\n▶️  {step_name}...")
            if not step_func():
                self.print_error(f"Setup gagal pada step: {step_name}")
                return False
        
        # Tanya apakah mau insert sample data
        print(f"\n{self.COLORS['WARNING']}{'='*60}{self.COLORS['ENDC']}")
        insert_sample = input(f"{self.COLORS['WARNING']}Masukkan data contoh? (y/n): {self.COLORS['ENDC']}").strip().lower()
        
        if insert_sample == 'y':
            print(f"\n▶️  Memasukkan data contoh...")
            if not self.insert_sample_data():
                self.print_warning("Gagal memasukkan data contoh, tetapi database sudah dibuat")
        else:
            self.print_info("Data contoh tidak dimasukkan")
        
        # Close connection and reconnect with database
        if self.connection:
            self.connection.close()
        
        if not self.connect_with_db():
            self.print_error("Gagal reconnect ke database")
            return False
        
        self.print_header("SETUP BERHASIL!")
        print(f"\n✅ Database '{self.database_name}' berhasil dibuat dan siap digunakan!")
        print(f"\n📁 Total tabel yang dibuat: 9 tabel dengan relasi lengkap")
        print(f"📊 Data contoh dimasukkan: Ya" if insert_sample == 'y' else "📊 Data contoh dimasukkan: Tidak")
        
        print(f"\n{self.COLORS['BOLD']}Selanjutnya:{self.COLORS['ENDC']}")
        print("1. Jalankan aplikasi: python main.py")
        print("2. Cek database: python database/check_database.py")
        print("3. Mulai gunakan sistem rental mobil!")
        
        return True

def main():
    """Fungsi utama untuk menjalankan script setup database"""
    
    # Banner
    print(f"""
    {chr(0x1F698)} {chr(0x1F4BE)} {chr(0x1F4C8)} {chr(0x1F4BB)} {chr(0x1F4D1)}
    ╔══════════════════════════════════════════════════════════╗
    ║          SISTEM RENTAL MOBIL - DATABASE SETUP           ║
    ║          Python OOP dengan SOLID & DRY Principles       ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Input credentials
    print("\n📝 Masukkan konfigurasi database MySQL:")
    print("-" * 50)
    
    host = input("MySQL Host [localhost]: ").strip() or 'localhost'
    user = input("MySQL Username [root]: ").strip() or 'root'
    
    # Try to connect without password first
    password = None
    try:
        # Try without password
        test_conn = mysql.connector.connect(host=host, user=user)
        test_conn.close()
        print("✓ Berhasil terhubung tanpa password")
    except:
        # Ask for password
        password = getpass.getpass("MySQL Password: ")
    
    # Create database creator instance
    db_creator = DatabaseCreator(host, user, password)
    
    # Run setup
    try:
        db_creator.run_all_setup()
    except KeyboardInterrupt:
        print(f"\n\n{chr(0x1F6AB)} Setup dibatalkan oleh user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{chr(0x1F6AB)} Error tidak terduga: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()