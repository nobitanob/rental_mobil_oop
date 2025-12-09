-- Create database
CREATE DATABASE IF NOT EXISTS rental_mobil_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE rental_mobil_db;

-- Tabel Mobil
CREATE TABLE IF NOT EXISTS mobil (
    id INT PRIMARY KEY AUTO_INCREMENT,
    merk VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    tahun INT NOT NULL,
    plat_nomor VARCHAR(20) UNIQUE NOT NULL,
    harga_sewa_per_hari DECIMAL(10,2) NOT NULL,
    status ENUM('tersedia', 'disewa', 'perbaikan') DEFAULT 'tersedia',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_merk (merk)
) ENGINE=InnoDB;

-- Tabel Pelanggan
CREATE TABLE IF NOT EXISTS pelanggan (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nik VARCHAR(20) UNIQUE NOT NULL,
    nama VARCHAR(100) NOT NULL,
    alamat TEXT,
    no_telepon VARCHAR(15),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nik (nik)
) ENGINE=InnoDB;

-- Tabel Penyewaan
CREATE TABLE IF NOT EXISTS penyewaan (
    id INT PRIMARY KEY AUTO_INCREMENT,
    mobil_id INT NOT NULL,
    pelanggan_id INT NOT NULL,
    tanggal_sewa DATE NOT NULL,
    tanggal_kembali DATE NOT NULL,
    tanggal_pengembalian DATE,
    total_hari INT NOT NULL,
    total_biaya DECIMAL(12,2) NOT NULL,
    denda DECIMAL(10,2) DEFAULT 0,
    status ENUM('aktif', 'selesai', 'terlambat') DEFAULT 'aktif',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mobil_id) REFERENCES mobil(id) ON DELETE RESTRICT,
    FOREIGN KEY (pelanggan_id) REFERENCES pelanggan(id) ON DELETE RESTRICT,
    INDEX idx_status (status),
    INDEX idx_tanggal_sewa (tanggal_sewa),
    INDEX idx_pelanggan (pelanggan_id)
) ENGINE=InnoDB;

-- Tabel Pembayaran
CREATE TABLE IF NOT EXISTS pembayaran (
    id INT PRIMARY KEY AUTO_INCREMENT,
    penyewaan_id INT NOT NULL,
    jumlah DECIMAL(12,2) NOT NULL,
    metode_pembayaran ENUM('tunai', 'transfer', 'kartu_kredit') NOT NULL,
    status ENUM('pending', 'lunas', 'gagal') DEFAULT 'pending',
    tanggal_bayar TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bukti_pembayaran TEXT,
    FOREIGN KEY (penyewaan_id) REFERENCES penyewaan(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_tanggal_bayar (tanggal_bayar)
) ENGINE=InnoDB;

-- Sample data
INSERT IGNORE INTO mobil (merk, model, tahun, plat_nomor, harga_sewa_per_hari, status) VALUES
('Toyota', 'Avanza', 2022, 'B 1234 ABC', 300000, 'tersedia'),
('Honda', 'Brio', 2021, 'B 5678 DEF', 250000, 'tersedia'),
('Mitsubishi', 'Xpander', 2023, 'B 9012 GHI', 400000, 'tersedia'),
('Suzuki', 'Ertiga', 2020, 'B 3456 JKL', 280000, 'disewa'),
('Toyota', 'Fortuner', 2022, 'B 7890 MNO', 600000, 'tersedia');

INSERT IGNORE INTO pelanggan (nik, nama, alamat, no_telepon, email) VALUES
('1234567890123456', 'Budi Santoso', 'Jl. Merdeka No. 1', '081234567890', 'budi@email.com'),
('2345678901234567', 'Siti Rahayu', 'Jl. Sudirman No. 45', '082345678901', 'siti@email.com'),
('3456789012345678', 'Ahmad Wijaya', 'Jl. Thamrin No. 12', '083456789012', 'ahmad@email.com');