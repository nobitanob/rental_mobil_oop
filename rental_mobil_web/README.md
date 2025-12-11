# 🚗 Rental Mobil Web - Django Application

Aplikasi web untuk sistem rental mobil berbasis Django Framework.

---

## 📁 Struktur Folder & Fungsi File

```
rental_mobil_web/
├── manage.py                    # Entry point Django CLI
├── rental/                      # Aplikasi utama rental
│   ├── __init__.py             # Package initializer
│   ├── admin.py                # Konfigurasi Django Admin Panel
│   ├── apps.py                 # Konfigurasi aplikasi
│   ├── models.py               # Model database (Mobil, Pelanggan, dll)
│   ├── views.py                # Logic tampilan/halaman
│   ├── tests.py                # Unit testing
│   └── migrations/             # File migrasi database
│       └── __init__.py
└── rental_mobil_web/           # Konfigurasi project
    ├── __init__.py             # Package initializer
    ├── settings.py             # Pengaturan Django (database, apps, dll)
    ├── urls.py                 # Routing URL utama
    ├── wsgi.py                 # WSGI entry point (production)
    └── asgi.py                 # ASGI entry point (async)
```

---

## 📄 Penjelasan Detail Setiap File

### 🔧 File Konfigurasi Project

| File | Fungsi |
|------|--------|
| `manage.py` | Command-line utility untuk menjalankan perintah Django seperti `runserver`, `migrate`, `createsuperuser` |
| `rental_mobil_web/settings.py` | Konfigurasi utama: database MySQL, timezone, installed apps, middleware |
| `rental_mobil_web/urls.py` | Mendefinisikan URL routing utama aplikasi |
| `rental_mobil_web/wsgi.py` | Entry point untuk deployment production (Apache/Nginx) |
| `rental_mobil_web/asgi.py` | Entry point untuk async server (Daphne/Uvicorn) |

### 📦 Aplikasi Rental

| File | Fungsi |
|------|--------|
| `rental/models.py` | Mendefinisikan struktur tabel database: **Mobil**, **Pelanggan**, **Penyewaan**, **Pembayaran** |
| `rental/admin.py` | Mengatur tampilan & fitur panel admin untuk setiap model |
| `rental/views.py` | Berisi logic untuk menampilkan halaman web (akan dikembangkan) |
| `rental/apps.py` | Konfigurasi metadata aplikasi rental |
| `rental/tests.py` | File untuk menulis unit test |
| `rental/migrations/` | Folder berisi file migrasi perubahan struktur database |

---

## 🗄️ Model Database

### 1. Mobil
Menyimpan data kendaraan yang tersedia untuk disewa.

| Field | Tipe | Keterangan |
|-------|------|------------|
| `id` | Integer | Primary key (auto) |
| `merk` | CharField | Merk mobil (Toyota, Honda, dll) |
| `model` | CharField | Model mobil (Avanza, Jazz, dll) |
| `tahun` | Integer | Tahun produksi |
| `plat_nomor` | CharField | Nomor plat (unik) |
| `harga_sewa_per_hari` | Decimal | Harga sewa per hari |
| `status` | CharField | tersedia / disewa / perbaikan |

### 2. Pelanggan
Menyimpan data pelanggan yang menyewa mobil.

| Field | Tipe | Keterangan |
|-------|------|------------|
| `id` | Integer | Primary key (auto) |
| `nik` | CharField | NIK 16 digit (unik) |
| `nama` | CharField | Nama lengkap |
| `alamat` | TextField | Alamat pelanggan |
| `no_telepon` | CharField | Nomor telepon |
| `email` | EmailField | Email pelanggan |

### 3. Penyewaan
Menyimpan data transaksi penyewaan.

| Field | Tipe | Keterangan |
|-------|------|------------|
| `id` | Integer | Primary key (auto) |
| `kode_penyewaan` | CharField | Kode unik (RNT-YYYYMMDD-XXXX) |
| `mobil` | ForeignKey | Relasi ke tabel Mobil |
| `pelanggan` | ForeignKey | Relasi ke tabel Pelanggan |
| `tanggal_sewa` | DateField | Tanggal mulai sewa |
| `tanggal_kembali` | DateField | Tanggal rencana kembali |
| `tanggal_pengembalian` | DateField | Tanggal aktual pengembalian |
| `total_hari` | Integer | Jumlah hari sewa |
| `total_biaya` | Decimal | Total biaya sewa |
| `denda` | Decimal | Denda keterlambatan |
| `status` | CharField | aktif / selesai / terlambat |

### 4. Pembayaran
Menyimpan data pembayaran.

| Field | Tipe | Keterangan |
|-------|------|------------|
| `id` | Integer | Primary key (auto) |
| `penyewaan` | ForeignKey | Relasi ke tabel Penyewaan |
| `jumlah` | Decimal | Jumlah pembayaran |
| `metode_pembayaran` | CharField | tunai / transfer / kartu_kredit |
| `status` | CharField | pending / lunas / gagal |
| `bukti_pembayaran` | CharField | Path file bukti (opsional) |

---

## 🚀 Cara Menggunakan

### Prasyarat
- Python 3.10+
- MySQL Server (Laragon/XAMPP)
- Database `rental_mobil_db` sudah ada

### 1. Install Dependencies

```bash
pip install django mysqlclient
```

### 2. Masuk ke Folder Project

```bash
cd d:\python\rental_mobil_oop\rental_mobil_web
```

### 3. Jalankan Migrasi (Jika Pertama Kali)

```bash
python manage.py migrate
```

### 4. Buat Superuser Admin (Jika Belum Ada)

```bash
python manage.py createsuperuser
```

### 5. Jalankan Server Development

```bash
python manage.py runserver
```

### 6. Akses Aplikasi

| URL | Keterangan |
|-----|------------|
| http://127.0.0.1:8000/ | Halaman utama (coming soon) |
| http://127.0.0.1:8000/admin/ | Panel Admin |

---

## 🔐 Login Admin Panel

- **URL:** http://127.0.0.1:8000/admin/
- **Username:** `admin`
- **Password:** `admin123`

### Fitur Admin Panel:
1. **Daftar Mobil** - Tambah, edit, hapus, filter mobil
2. **Daftar Pelanggan** - Kelola data pelanggan
3. **Daftar Penyewaan** - Lihat & kelola transaksi sewa
4. **Daftar Pembayaran** - Kelola pembayaran

---

## 📝 Perintah Django Berguna

| Perintah | Fungsi |
|----------|--------|
| `python manage.py runserver` | Jalankan development server |
| `python manage.py runserver 0.0.0.0:8000` | Jalankan & akses dari jaringan lokal |
| `python manage.py migrate` | Terapkan migrasi database |
| `python manage.py makemigrations` | Buat file migrasi baru |
| `python manage.py createsuperuser` | Buat akun admin |
| `python manage.py shell` | Buka Django shell interaktif |
| `python manage.py collectstatic` | Kumpulkan static files (production) |

---

## 🔗 Koneksi Database

Aplikasi ini terhubung ke database MySQL yang sama dengan aplikasi CLI:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rental_mobil_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

## 🔄 Sinkronisasi dengan CLI

Aplikasi web dan CLI menggunakan database yang sama, sehingga:
- Data yang ditambah di CLI akan muncul di web
- Data yang ditambah di web akan muncul di CLI
- Kedua aplikasi bisa berjalan bersamaan

---

## 📌 Catatan Penting

1. **managed = False** - Model Django tidak akan membuat/mengubah struktur tabel karena tabel sudah dibuat oleh CLI
2. **Timezone** - Menggunakan `Asia/Jakarta`
3. **Debug Mode** - Aktif (jangan digunakan di production)

---

## 🛠️ Pengembangan Selanjutnya

- [ ] Halaman frontend untuk pelanggan
- [ ] Form penyewaan online
- [ ] Dashboard statistik
- [ ] API REST untuk integrasi
- [ ] Authentication pelanggan
- [ ] Notifikasi email

---

## 📞 Kontak

Untuk pertanyaan atau bantuan, hubungi developer.
