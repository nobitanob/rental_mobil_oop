Sistem manajemen rental mobil yang dibangun dengan Python menggunakan prinsip OOP, SOLID, dan DRY. Proyek ini dilengkapi dengan koneksi database MySQL dan arsitektur yang modular.

📋 Fitur Utama
✅ Manajemen Mobil - CRUD lengkap untuk data kendaraan

✅ Manajemen Pelanggan - Data pelanggan dengan validasi NIK

✅ Transaksi Penyewaan - Sistem sewa dengan perhitungan otomatis

✅ Pengembalian & Denda - Perhitungan denda keterlambatan otomatis

✅ Sistem Pembayaran - Multi-metode pembayaran

✅ Laporan - Laporan harian dan statistik

✅ Database Relasional - 4 tabel dengan relasi yang solid

✅ Prinsip SOLID - Implementasi lengkap 5 prinsip SOLID

✅ DRY Code - Tidak ada duplikasi kode

✅ Reusable Modules - Modul yang dapat digunakan kembali

🏗️ Arsitektur Proyek
text
rental-mobil-oop/
├── 📂 database/
│   ├── create_database.py      # Script setup database
│   ├── setup_simple.py         # Setup versi sederhana
│   ├── check_database.py       # Cek status database
│   └── connection.py           # Koneksi database dengan pooling
├── 📂 models/
│   ├── entities.py             # Entity classes (Mobil, Pelanggan, dll)
│   └── repositories.py         # Repository pattern untuk CRUD
├── 📂 services/
│   └── rental_service.py       # Business logic layer
├── 📂 utils/
│   └── validators.py           # Reusable validation functions
├── config.py                   # Konfigurasi aplikasi
├── main.py                     # Aplikasi utama (CLI)
├── requirements.txt            # Dependencies
├── .env.example                # Template environment variables
└── README.md                   # Dokumentasi ini