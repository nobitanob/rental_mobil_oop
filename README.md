# 🚗 Rental Mobil CLI - Aplikasi Command Line Interface

Aplikasi CLI untuk sistem rental mobil berbasis OOP (Object-Oriented Programming) dengan MySQL database.

---

## 📁 Struktur Folder & Fungsi File

```
rental_mobil_cli/
├── main.py                      # Entry point aplikasi CLI
├── config.py                    # Konfigurasi database & environment
├── requirements.txt             # Dependencies & library yang diperlukan
├── .env                         # File environment variables (tidak di-track git)
├── .env.example                 # Contoh file environment variables
├── database/                    # Modul database
│   ├── __init__.py             # Package initializer
│   ├── connection.py           # Manager koneksi database
│   ├── setup_database.py       # Script setup database otomatis
│   ├── create_database.py      # Alternative untuk membuat database
│   └── queries.sql             # Raw SQL queries (opsional)
├── models/                      # Modul data entities & repositories
│   ├── __init__.py             # Package initializer
│   ├── entitas.py              # Class Entity (Mobil, Pelanggan, dll)
│   └── repositories.py         # Repository Pattern (CRUD operations)
├── services/                    # Modul business logic
│   ├── __init__.py             # Package initializer
│   └── rental_service.py       # Layanan rental (transaksi, pembayaran, dll)
└── utils/                       # Modul utility & helper
    ├── __init__.py             # Package initializer
    └── validators.py           # Validasi data input
```

---

## 📄 Penjelasan Detail Setiap File

### 🔧 File Konfigurasi & Entry Point

| File | Fungsi |
|------|--------|
| `main.py` | Entry point utama, berisi class `RentalMobilApp` dengan menu interaktif |
| `config.py` | Menyimpan konfigurasi database dari file `.env` menggunakan `python-dotenv` |
| `requirements.txt` | Daftar semua dependencies yang diperlukan |
| `.env` | File environment (lokal, tidak di-commit) - berisi DB_HOST, DB_USER, dll |
| `.env.example` | Template file `.env` untuk referensi developer lain |

### 📦 Database Module

| File | Fungsi |
|------|--------|
| `connection.py` | Class `DatabaseManager` untuk mengelola koneksi MySQL |
| `setup_database.py` | Fungsi `setup_database_simple()` untuk membuat database & tabel otomatis |
| `create_database.py` | Alternative script untuk membuat database |
| `queries.sql` | Berisi raw SQL queries jika diperlukan manual query |

### 📦 Models Module

| File | Fungsi |
|------|--------|
| `entitas.py` | Mendefinisikan class Entity untuk Mobil, Pelanggan, Penyewaan, Pembayaran |
| `repositories.py` | Implementasi Repository Pattern (CRUD) untuk setiap entity |

### 📦 Services Module

| File | Fungsi |
|------|--------|
| `rental_service.py` | Business logic rental: sewa mobil, pengembalian, pembayaran, laporan |

### 📦 Utils Module

| File | Fungsi |
|------|--------|
| `validators.py` | Class `Validator` dengan method untuk validasi data (NIK, email, telepon, dll) |

---

## 🗄️ Model Entity & Database

### 1. Mobil
Menyimpan data kendaraan yang tersedia untuk disewa.

| Field | Tipe | Keterangan |
|-------|------|------------|
| `id` | INT | Primary key (auto increment) |
| `merk` | VARCHAR(100) | Merk mobil (Toyota, Honda, dll) |
| `model` | VARCHAR(100) | Model mobil (Avanza, Jazz, dll) |
| `tahun` | INT | Tahun produksi |
| `plat_nomor` | VARCHAR(20) | Nomor plat (unik) |
| `harga_sewa_per_hari` | DECIMAL(10,2) | Harga sewa per hari |
| `status` | VARCHAR(20) | tersedia / disewa / perbaikan |
| `created_at` | TIMESTAMP | Waktu data dibuat |
| `updated_at` | TIMESTAMP | Waktu data diperbarui |

### 2. Pelanggan
Menyimpan data pelanggan yang menyewa mobil.

| Field | Tipe | Keterangan |
|-------|------|------------|
| `id` | INT | Primary key (auto increment) |
| `nik` | VARCHAR(16) | NIK 16 digit (unik) |
| `nama` | VARCHAR(255) | Nama lengkap |
| `alamat` | TEXT | Alamat pelanggan |
| `no_telepon` | VARCHAR(20) | Nomor telepon |
| `email` | VARCHAR(255) | Email pelanggan |
| `created_at` | TIMESTAMP | Waktu data dibuat |
| `updated_at` | TIMESTAMP | Waktu data diperbarui |

### 3. Penyewaan
Menyimpan data transaksi penyewaan mobil.

| Field | Tipe | Keterangan |
|-------|------|------------|
| `id` | INT | Primary key (auto increment) |
| `kode_penyewaan` | VARCHAR(50) | Kode unik (RENT-YYYYMM-XXXX) |
| `mobil_id` | INT | Foreign key ke tabel Mobil |
| `pelanggan_id` | INT | Foreign key ke tabel Pelanggan |
| `tanggal_sewa` | DATE | Tanggal mulai sewa |
| `tanggal_kembali` | DATE | Tanggal rencana pengembalian |
| `tanggal_pengembalian` | DATE | Tanggal aktual pengembalian (nullable) |
| `total_hari` | INT | Jumlah hari sewa |
| `total_biaya` | DECIMAL(12,2) | Total biaya sewa |
| `denda` | DECIMAL(12,2) | Denda keterlambatan |
| `status` | VARCHAR(20) | aktif / selesai / terlambat |
| `created_at` | TIMESTAMP | Waktu data dibuat |
| `updated_at` | TIMESTAMP | Waktu data diperbarui |

### 4. Pembayaran
Menyimpan data pembayaran dari transaksi penyewaan.

| Field | Tipe | Keterangan |
|-------|------|------------|
| `id` | INT | Primary key (auto increment) |
| `penyewaan_id` | INT | Foreign key ke tabel Penyewaan |
| `jumlah` | DECIMAL(12,2) | Jumlah pembayaran |
| `metode_pembayaran` | VARCHAR(50) | tunai / transfer / kartu_kredit |
| `status` | VARCHAR(20) | pending / lunas / gagal |
| `bukti_pembayaran` | VARCHAR(255) | Path/nama file bukti (nullable) |
| `created_at` | TIMESTAMP | Waktu data dibuat |
| `updated_at` | TIMESTAMP | Waktu data diperbarui |

---

## 🏗️ Arsitektur & Design Pattern

### 1. **Object-Oriented Programming (OOP)**
- Menggunakan class untuk merepresentasikan entities
- Encapsulation & abstraction untuk logika bisnis

### 2. **Repository Pattern**
- Separasi antara data access layer dan business logic
- Setiap entity memiliki repository sendiri (Mobil, Pelanggan, Penyewaan, Pembayaran)

### 3. **Single Responsibility Principle**
- Setiap class memiliki satu tanggung jawab
- `DatabaseManager`: Mengelola koneksi
- `RentalService`: Mengelola bisnis logic rental
- `*Repository`: Mengelola CRUD operations

### 4. **Validator Pattern**
- Validasi terpusat di class `Validator`
- Validasi untuk NIK, email, telepon, license plate, dll

---

## 🚀 Cara Menggunakan

### Prasyarat
- Python 3.8+
- MySQL Server (XAMPP, Laragon, atau standalone MySQL)
- Pip package manager

### 1. Setup Environment

Buat file `.env` di folder `rental_mobil_cli`:

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=rental_mobil_db
```

### 2. Install Dependencies

```bash
cd d:\rental_mobil_oop\rental_mobil_cli
pip install -r requirements.txt
```

Atau install manual:

```bash
pip install mysql-connector-python==8.1.0 python-dotenv==1.0.0
```

### 3. Setup Database (Pertama Kali)

```bash
python main.py
```

Kemudian pilih menu **8. Setup Database** untuk membuat database & tabel otomatis.

Atau manual setup:

```python
from database.setup_database import setup_database_simple
setup_database_simple()
```

### 4. Jalankan Aplikasi

```bash
python main.py
```

### 5. Menu Aplikasi

```
==================================================
SISTEM RENTAL MOBIL OOP
==================================================
1. Kelola Mobil
2. Kelola Pelanggan
3. Sewa Mobil
4. Pengembalian Mobil
5. Pembayaran
6. Laporan Harian
7. Cari Mobil Tersedia
8. Setup Database
0. Keluar
==================================================
```

---

## 📋 Fitur-Fitur Utama

### 1. Kelola Mobil
- **Tambah Mobil** - Input merk, model, tahun, plat nomor, harga
- **Lihat Daftar Mobil** - Tampilkan semua mobil
- **Edit Mobil** - Ubah data mobil yang ada
- **Hapus Mobil** - Hapus data mobil
- **Cari Mobil** - Cari berdasarkan merk atau model

### 2. Kelola Pelanggan
- **Tambah Pelanggan** - Input NIK, nama, alamat, telepon, email
- **Lihat Daftar Pelanggan** - Tampilkan semua pelanggan
- **Edit Pelanggan** - Ubah data pelanggan
- **Hapus Pelanggan** - Hapus data pelanggan
- **Cari Pelanggan** - Cari berdasarkan NIK atau nama

### 3. Sewa Mobil
- **Proses Penyewaan** - Input pelanggan, pilih mobil, tentukan durasi
- **Validasi Otomatis** - Cek ketersediaan mobil, hitung total biaya
- **Generate Kode Penyewaan** - Otomatis generate kode unik (RENT-YYYYMM-XXXX)

### 4. Pengembalian Mobil
- **Proses Pengembalian** - Input kode penyewaan, tanggal pengembalian
- **Hitung Denda** - Otomatis hitung denda jika terlambat
- **Update Status Mobil** - Ubah status mobil menjadi "tersedia"

### 5. Pembayaran
- **Proses Pembayaran** - Input metode pembayaran (tunai/transfer/kartu kredit)
- **Kelola Bukti Pembayaran** - Simpan path file bukti
- **Tracking Status** - Lihat status pembayaran (pending/lunas/gagal)

### 6. Laporan Harian
- **Total Penyewaan** - Jumlah penyewaan hari ini
- **Total Pendapatan** - Perhitungan total biaya + denda
- **Mobil Tersedia/Disewa** - Statistik status mobil
- **Export ke File** - Simpan laporan dalam format text/CSV

### 7. Cari Mobil Tersedia
- **Filter Berdasarkan Tanggal** - Cari mobil yang tersedia di tanggal tertentu
- **Filter Berdasarkan Harga** - Cari mobil dalam range harga

---

## 🔐 Validasi Data

Class `Validator` menyediakan method validasi:

| Method | Fungsi |
|--------|--------|
| `validate_nik(nik)` | Validasi NIK 16 digit |
| `validate_email(email)` | Validasi format email |
| `validate_phone(phone)` | Validasi nomor telepon |
| `validate_license_plate(plate)` | Validasi format plat nomor |
| `validate_year(year)` | Validasi tahun produksi |
| `validate_positive_number(num, field)` | Validasi angka positif |
| `validate_not_empty(value, field)` | Validasi tidak kosong |
| `validate_in_list(value, list, field)` | Validasi dalam daftar pilihan |

---

## 🔗 Koneksi Database

### File: `config.py`

```python
class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'rental_mobil_db')
```

### File: `database/connection.py`

Menggunakan MySQL Connector untuk Python:

```python
import mysql.connector
from config import Config

connection = mysql.connector.connect(**Config.get_db_config())
cursor = connection.cursor()
```

---

## 📚 Class & Method Penting

### Entity Classes

#### `Mobil`
```python
mobil = Mobil(
    merk="Toyota",
    model="Avanza",
    tahun=2023,
    plat_nomor="AB 1234 CD",
    harga_sewa_per_hari=300000.00,
    status="tersedia"
)
mobil.validate()  # Validasi data
```

#### `Pelanggan`
```python
pelanggan = Pelanggan(
    nik="1234567890123456",
    nama="John Doe",
    alamat="Jl. Merdeka No. 1",
    no_telepon="081234567890",
    email="john@example.com"
)
```

### Repository Classes

#### `MobilRepository`
```python
mobil_repo = MobilRepository(db_manager)

# Create
new_mobil = Mobil(...)
mobil_repo.create(new_mobil)

# Read
mobil = mobil_repo.find_by_id(1)
all_mobil = mobil_repo.find_all()

# Update
mobil_repo.update(mobil)

# Delete
mobil_repo.delete(1)

# Custom
tersedia = mobil_repo.find_by_status('tersedia')
```

### Service Class

#### `RentalService`
```python
rental_service = RentalService(
    mobil_repo, pelanggan_repo,
    penyewaan_repo, pembayaran_repo
)

# Sewa mobil
penyewaan = rental_service.create_penyewaan(
    mobil_id=1,
    pelanggan_id=1,
    tanggal_sewa=date.today(),
    tanggal_kembali=date.today() + timedelta(days=3)
)

# Pengembalian
rental_service.process_pengembalian(
    penyewaan_id=1,
    tanggal_pengembalian=date.today()
)

# Pembayaran
rental_service.process_pembayaran(
    penyewaan_id=1,
    jumlah=900000,
    metode='tunai'
)
```

---

## 🔄 Sinkronisasi dengan Django Web

Aplikasi CLI dan Django Web menggunakan **database yang sama**, sehingga:

✅ Data yang ditambah di CLI akan muncul di Django Admin  
✅ Data yang ditambah di Django akan muncul di CLI  
✅ Kedua aplikasi dapat berjalan bersamaan tanpa konflik  
✅ Table structure sama di kedua aplikasi  

---

## ⚡ Contoh Penggunaan

### Contoh 1: Menambah Mobil Baru

```python
from main import RentalMobilApp

app = RentalMobilApp()

# Masuk ke menu Kelola Mobil (pilihan 1)
# Input data mobil:
# - Merk: Toyota
# - Model: Avanza
# - Tahun: 2023
# - Plat Nomor: AB 1234 CD
# - Harga Sewa: 300000
```

### Contoh 2: Proses Penyewaan

```python
# Dari menu aplikasi:
# 1. Pilih "Sewa Mobil" (pilihan 3)
# 2. Input NIK pelanggan
# 3. Pilih mobil dari daftar tersedia
# 4. Input tanggal sewa dan kembali
# 5. Sistem otomatis hitung total hari & biaya
# 6. Kode penyewaan otomatis generate
```

### Contoh 3: Pengembalian & Pembayaran

```python
# 1. Pilih "Pengembalian Mobil" (pilihan 4)
# 2. Input kode penyewaan
# 3. Input tanggal pengembalian aktual
# 4. Sistem hitung denda jika terlambat
# 5. Pilih "Pembayaran" (pilihan 5)
# 6. Input jumlah pembayaran
# 7. Pilih metode pembayaran
```

---

## 🐛 Troubleshooting

### Error: "Could not find module 'mysql'"
**Solusi:**
```bash
pip install mysql-connector-python
```

### Error: "Access denied for user 'root'"
**Solusi:** Cek file `.env` dan pastikan `DB_USER` dan `DB_PASSWORD` sesuai dengan MySQL Anda.

### Error: "Database 'rental_mobil_db' does not exist"
**Solusi:** Jalankan menu Setup Database (pilihan 8) dari aplikasi CLI.

### Connection Timeout
**Solusi:** Pastikan MySQL Server berjalan dan dapat diakses dari localhost.

---

## 🛠️ Development & Extension

### Cara Menambah Fitur Baru

1. **Buat Entity Class** di `models/entitas.py`
2. **Buat Repository** di `models/repositories.py`
3. **Tambah Business Logic** di `services/rental_service.py`
4. **Tambah Menu** di `main.py`
5. **Tambah Validasi** di `utils/validators.py` (jika perlu)

### Contoh: Menambah Fitur "Asuransi"

```python
# 1. Entitas
class Asuransi(Entity):
    def __init__(self, penyewaan_id, tipe, harga, status='aktif', **kwargs):
        self.penyewaan_id = penyewaan_id
        self.tipe = tipe
        self.harga = harga
        self.status = status

# 2. Repository
class AsuransiRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, 'asuransi', Asuransi)

# 3. Service
def create_asuransi(self, penyewaan_id, tipe, harga):
    asuransi = Asuransi(penyewaan_id, tipe, harga)
    return self.asuransi_repo.create(asuransi)
```

---

## 📊 ERD (Entity Relationship Diagram)

```
┌─────────────────┐
│     MOBIL       │
├─────────────────┤
│ id (PK)         │
│ merk            │
│ model           │
│ tahun           │
│ plat_nomor (U)  │
│ harga_sewa      │
│ status          │
└────────┬────────┘
         │
         │ 1:M
         │
┌────────▼──────────────┐
│   PENYEWAAN           │
├───────────────────────┤
│ id (PK)               │
│ kode_penyewaan (U)    │
│ mobil_id (FK)         │
│ pelanggan_id (FK)     │
│ tanggal_sewa          │
│ tanggal_kembali       │
│ tanggal_pengembalian  │
│ total_hari            │
│ total_biaya           │
│ denda                 │
│ status                │
└────────┬──────────────┘
         │
         │ 1:M
         │
┌────────▼──────────────┐
│    PEMBAYARAN         │
├───────────────────────┤
│ id (PK)               │
│ penyewaan_id (FK)     │
│ jumlah                │
│ metode_pembayaran     │
│ status                │
│ bukti_pembayaran      │
└───────────────────────┘

┌─────────────────┐
│   PELANGGAN     │
├─────────────────┤
│ id (PK)         │
│ nik (U)         │
│ nama            │
│ alamat          │
│ no_telepon      │
│ email           │
└────────┬────────┘
         │
         │ 1:M
         │
    (PENYEWAAN)
```

---

## 📌 Catatan Penting

1. **Database Consistency** - CLI dan Django Web berbagi database yang sama
2. **Transaction Safety** - Gunakan connection.commit() untuk memastikan data tersimpan
3. **Error Handling** - Selalu gunakan try-catch untuk database operations
4. **Input Validation** - Semua input melalui Validator sebelum disimpan
5. **Status Tracking** - Mobil otomatis berubah status saat disewa/dikembalikan

---

## 🔄 Version Control System (Data Versioning)

Sistem ini memiliki fitur version control internal untuk melacak perubahan data dengan kemampuan commit dan rollback.

### File Terkait:
| File | Lokasi | Fungsi |
|------|--------|--------|
| `version_control.py` | `rental_mobil_web/rental/` | Service class untuk commit/rollback |
| `models.py` (DataVersion) | `rental_mobil_web/rental/` | Model untuk menyimpan versi data |

### Fitur:
- ✅ **Commit** - Simpan snapshot data sebelum/setelah perubahan
- ✅ **Rollback** - Kembalikan data ke versi sebelumnya
- ✅ **History** - Lihat riwayat semua perubahan
- ✅ **Compare** - Bandingkan dua versi
- ✅ **Branch** - Buat cabang eksperimental

### Penggunaan di Code:

```python
from rental.version_control import VCS
from rental.models import Mobil

# Commit sebelum update
mobil = Mobil.objects.get(pk=1)
VCS.commit(mobil, "Sebelum ubah harga", user="admin")

# Update dan commit setelah perubahan
mobil.harga_sewa_per_hari = 500000
mobil.save()
VCS.commit_update(mobil, "Harga diupdate ke 500rb", user="admin")

# Rollback ke versi tertentu
VCS.rollback("Mobil", object_id=1, version=2, user="admin")

# Lihat history
history = VCS.get_history("Mobil", object_id=1)
for v in history:
    print(f"v{v.version}: {v.commit_message}")

# Bandingkan versi
diff = VCS.compare_versions(version1, version2)
```

### CLI Commands:

```powershell
# Lihat history versi
python rental/version_control.py history Mobil 1

# Rollback ke versi tertentu
python rental/version_control.py rollback Mobil 1 2

# Bersihkan versi lama (simpan 5 terakhir)
python rental/version_control.py cleanup 5

# Lihat statistik
python rental/version_control.py stats
```

### Django Admin:
Akses `/admin/rental/dataversion/` untuk:
- Lihat semua versi dengan badge aksi (➕ Create, ✏️ Update, 🗑️ Delete, 📝 Commit, ↩️ Rollback)
- Filter by model, action, branch, user
- Action "Rollback ke versi ini"
- Detail perubahan dari versi sebelumnya

---

## 🔐 Keamanan

- ✅ Validasi input di setiap operation
- ✅ Environment variables untuk kredensial database
- ✅ Prepared statements untuk mencegah SQL injection
- ✅ Transaction management untuk data integrity
- ✅ Error handling tanpa expose sensitive data

---

## 📞 Support & Dokumentasi

Untuk pertanyaan lebih lanjut, lihat:
- README.md di folder `rental_mobil_web`
- Docstring di setiap class dan method
- File `.env.example` untuk konfigurasi

---

**Last Updated:** December 2024  
**Version:** 1.0.0  
**License:** MIT