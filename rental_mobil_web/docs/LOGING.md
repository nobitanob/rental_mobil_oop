# Dokumentasi Fitur Logging dan Notifikasi

Dokumentasi ini menjelaskan fitur logging dan notifikasi yang ditambahkan pada aplikasi Rental Mobil Web.

---

## 📁 Daftar File yang Ditambahkan/Dimodifikasi

### File Baru

| File | Lokasi | Fungsi |
|------|--------|--------|
| `middleware.py` | `rental/` | Middleware untuk logging HTTP request dan keamanan |
| `services.py` | `rental/` | Service class untuk mengelola notifikasi |
| `signals.py` | `rental/` | Django signals untuk auto-logging dan auto-notifikasi |
| `cek_penyewaan.py` | `rental/management/commands/` | Management command untuk cek keterlambatan |

### File yang Dimodifikasi

| File | Lokasi | Perubahan |
|------|--------|-----------|
| `settings.py` | `rental_mobil_web/` | Konfigurasi logging, email, dan middleware |
| `models.py` | `rental/` | Tambah model `Notifikasi` dan `LogAktivitas` |
| `admin.py` | `rental/` | Tambah admin interface untuk Notifikasi dan LogAktivitas |
| `apps.py` | `rental/` | Load signals saat aplikasi ready |

---

## 📝 Penjelasan Detail Setiap File

### 1. `rental_mobil_web/settings.py`

**Fungsi:** Konfigurasi utama Django untuk logging dan email.

**Penambahan:**

```python
# Konfigurasi Logging
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {...},           # Log ke file rental_mobil.log
        'error_file': {...},     # Log error ke error.log
        'security_file': {...},  # Log keamanan ke security.log
    },
    'loggers': {
        'rental': {...},              # Logger utama aplikasi
        'rental.penyewaan': {...},    # Logger khusus penyewaan
        'rental.pembayaran': {...},   # Logger khusus pembayaran
        'rental.notifikasi': {...},   # Logger khusus notifikasi
    }
}

# Middleware untuk logging
MIDDLEWARE = [
    ...
    'rental.middleware.RequestLoggingMiddleware',
    'rental.middleware.SecurityLoggingMiddleware', 
    'rental.middleware.UserActivityMiddleware',
]

# Konfigurasi Email untuk notifikasi
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
```

**File Log yang Dihasilkan:**
- `logs/rental_mobil.log` - Log umum aplikasi
- `logs/error.log` - Log khusus error
- `logs/security.log` - Log keamanan

---

### 2. `rental/middleware.py`

**Fungsi:** Middleware untuk mencatat semua HTTP request/response dan aktivitas keamanan.

**Class yang tersedia:**

#### `RequestLoggingMiddleware`
Mencatat setiap HTTP request dan response.

```python
# Output log contoh:
# INFO 2025-12-13 10:00:00 Request: GET /admin/ - IP: 127.0.0.1 - User: admin
# INFO 2025-12-13 10:00:01 Response: GET /admin/ - Status: 200 - Duration: 150ms
```

#### `SecurityLoggingMiddleware`
Mendeteksi aktivitas mencurigakan seperti SQL injection.

```python
# Output log contoh:
# WARNING Potential SQL Injection attempt dari IP: 192.168.1.1 - Query: SELECT * FROM...
# INFO Admin access: GET /admin/rental/mobil/ - IP: 127.0.0.1 - User: admin
```

#### `UserActivityMiddleware`
Menyimpan informasi client (IP, user agent) untuk tracking aktivitas.

---

### 3. `rental/models.py`

**Fungsi:** Model database untuk menyimpan notifikasi dan log aktivitas.

#### Model `Notifikasi`

```python
class Notifikasi(models.Model):
    judul = models.CharField(max_length=200)
    pesan = models.TextField()
    tipe = models.CharField()      # info, warning, success, error
    kategori = models.CharField()  # penyewaan_baru, pembayaran, dll
    penyewaan_id_ref = models.IntegerField()  # Referensi ke penyewaan
    pelanggan_id_ref = models.IntegerField()  # Referensi ke pelanggan
    pelanggan_nama = models.CharField()
    dibaca = models.BooleanField(default=False)
    dikirim_email = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Tipe Notifikasi:**
| Tipe | Deskripsi |
|------|-----------|
| `info` | Informasi umum |
| `warning` | Peringatan |
| `success` | Sukses/berhasil |
| `error` | Error/gagal |

**Kategori Notifikasi:**
| Kategori | Deskripsi |
|----------|-----------|
| `penyewaan_baru` | Notifikasi penyewaan baru |
| `pembayaran` | Notifikasi pembayaran |
| `pengembalian` | Notifikasi pengembalian mobil |
| `keterlambatan` | Peringatan keterlambatan |
| `reminder` | Pengingat jatuh tempo |
| `sistem` | Notifikasi sistem |

#### Model `LogAktivitas`

```python
class LogAktivitas(models.Model):
    user = models.CharField(max_length=100)
    aksi = models.CharField()       # create, update, delete, login, logout
    model_name = models.CharField() # Nama model yang diubah
    object_id = models.IntegerField()
    object_repr = models.CharField()
    perubahan = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**Jenis Aksi:**
| Aksi | Deskripsi |
|------|-----------|
| `create` | Tambah data baru |
| `update` | Ubah data |
| `delete` | Hapus data |
| `view` | Lihat data |
| `login` | User login |
| `logout` | User logout |

---

### 4. `rental/services.py`

**Fungsi:** Service class untuk membuat dan mengirim notifikasi.

#### Class `NotifikasiService`

**Method yang tersedia:**

| Method | Fungsi |
|--------|--------|
| `buat_notifikasi()` | Membuat notifikasi baru |
| `kirim_email_notifikasi()` | Mengirim notifikasi via email |
| `notifikasi_penyewaan_baru()` | Notifikasi saat ada penyewaan baru |
| `notifikasi_pembayaran()` | Notifikasi saat pembayaran diterima |
| `notifikasi_pengembalian()` | Notifikasi saat mobil dikembalikan |
| `notifikasi_reminder_pengembalian()` | Reminder sebelum jatuh tempo |
| `notifikasi_keterlambatan()` | Peringatan keterlambatan |
| `get_notifikasi_belum_dibaca()` | Ambil notifikasi yang belum dibaca |
| `get_jumlah_notifikasi_belum_dibaca()` | Hitung notifikasi belum dibaca |
| `tandai_semua_dibaca()` | Tandai semua notifikasi sudah dibaca |

**Contoh Penggunaan:**

```python
from rental.services import NotifikasiService

# Buat notifikasi manual
NotifikasiService.buat_notifikasi(
    judul="Test Notifikasi",
    pesan="Ini adalah pesan test",
    tipe="info",
    kategori="sistem"
)

# Notifikasi penyewaan baru (otomatis kirim email)
NotifikasiService.notifikasi_penyewaan_baru(penyewaan_instance)

# Ambil notifikasi belum dibaca
notifikasi = NotifikasiService.get_notifikasi_belum_dibaca(limit=10)
```

---

### 5. `rental/signals.py`

**Fungsi:** Django signals untuk auto-logging dan auto-notifikasi saat data berubah.

**Signal yang terdaftar:**

| Signal | Model | Fungsi |
|--------|-------|--------|
| `post_save` | Mobil | Log saat mobil ditambah/diupdate |
| `post_delete` | Mobil | Log saat mobil dihapus |
| `post_save` | Pelanggan | Log saat pelanggan ditambah/diupdate |
| `post_delete` | Pelanggan | Log saat pelanggan dihapus |
| `post_save` | Penyewaan | Log + Notifikasi saat penyewaan dibuat/selesai |
| `post_delete` | Penyewaan | Log saat penyewaan dihapus |
| `post_save` | Pembayaran | Log + Notifikasi saat pembayaran dibuat |
| `post_delete` | Pembayaran | Log saat pembayaran dihapus |
| `user_logged_in` | User | Log saat user login |
| `user_logged_out` | User | Log saat user logout |
| `user_login_failed` | User | Log saat login gagal |

**Cara Kerja:**
- Signals otomatis dipanggil oleh Django saat ada operasi database
- Tidak perlu memanggil manual, cukup simpan data seperti biasa

```python
# Contoh: Simpan penyewaan baru
penyewaan = Penyewaan.objects.create(...)
# Signal otomatis:
# 1. Mencatat log ke LogAktivitas
# 2. Membuat Notifikasi "Penyewaan Baru"
# 3. Mengirim email ke pelanggan (jika dikonfigurasi)
```

---

### 6. `rental/management/commands/cek_penyewaan.py`

**Fungsi:** Management command untuk mengecek penyewaan yang akan jatuh tempo atau terlambat.

**Cara Penggunaan:**

```bash
# Cek penyewaan dengan reminder 1 hari sebelum jatuh tempo (default)
python manage.py cek_penyewaan

# Cek dengan reminder 3 hari sebelum jatuh tempo
python manage.py cek_penyewaan --reminder-days=3
```

**Yang Dilakukan Command Ini:**
1. Mencari penyewaan aktif yang akan jatuh tempo dalam X hari
2. Mengirim notifikasi reminder ke pelanggan
3. Mencari penyewaan yang sudah terlambat
4. Mengubah status menjadi "terlambat"
5. Menghitung estimasi denda
6. Mengirim notifikasi keterlambatan

**Contoh Output:**

```
Mengecek penyewaan aktif pada 2025-12-13...
  Reminder terkirim: RNT-20251210-0001
  Keterlambatan: RNT-20251205-0003 - 3 hari - Denda: Rp 450,000

Selesai!
  - Reminder terkirim: 1
  - Penyewaan terlambat: 1
```

**Otomatisasi dengan Cron Job (Linux) atau Task Scheduler (Windows):**

```bash
# Linux crontab - jalankan setiap hari jam 8 pagi
0 8 * * * cd /path/to/project && python manage.py cek_penyewaan
```

---

### 7. `rental/admin.py`

**Fungsi:** Konfigurasi admin interface untuk model Notifikasi dan LogAktivitas.

**Fitur Admin Notifikasi:**
- List view dengan badge status berwarna
- Filter berdasarkan tipe, kategori, status dibaca
- Search berdasarkan judul, pesan, nama pelanggan
- Action: "Tandai sebagai sudah dibaca" dan "Tandai sebagai belum dibaca"
- Date hierarchy berdasarkan tanggal dibuat

**Fitur Admin LogAktivitas:**
- List view dengan badge aksi berwarna
- Filter berdasarkan aksi, model, tanggal
- Search berdasarkan user, model, perubahan
- Read-only (tidak bisa edit/tambah)
- Hanya superuser yang bisa hapus log

---

### 8. `rental/apps.py`

**Fungsi:** Konfigurasi aplikasi Django dan load signals.

```python
class RentalConfig(AppConfig):
    name = 'rental'
    
    def ready(self):
        # Import signals saat aplikasi ready
        import rental.signals
```

---

## ⚙️ Konfigurasi Email (Opsional)

Untuk mengaktifkan notifikasi email, edit `settings.py`:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Gunakan App Password, bukan password biasa
```

**Cara Mendapatkan App Password Gmail:**
1. Buka Google Account → Security
2. Aktifkan 2-Step Verification
3. Buat App Password untuk "Mail"
4. Gunakan password yang digenerate

---

## 📊 Struktur Folder Logs

```
rental_mobil_web/
└── logs/
    ├── rental_mobil.log   # Log umum (max 5MB, 5 backup)
    ├── error.log          # Log error (max 5MB, 5 backup)
    └── security.log       # Log keamanan (max 5MB, 5 backup)
```

---

## 🔧 Contoh Penggunaan di Views

```python
import logging
from rental.services import NotifikasiService

logger = logging.getLogger('rental')

def proses_penyewaan(request):
    try:
        # Proses penyewaan...
        penyewaan = Penyewaan.objects.create(...)
        
        logger.info(f"Penyewaan berhasil dibuat: {penyewaan.kode_penyewaan}")
        
        # Notifikasi otomatis via signal, tapi bisa juga manual:
        # NotifikasiService.notifikasi_penyewaan_baru(penyewaan)
        
    except Exception as e:
        logger.error(f"Gagal membuat penyewaan: {str(e)}")
        raise
```

---

## 📌 Tips dan Best Practices

1. **Gunakan logger yang sesuai** untuk setiap modul:
   - `rental` - Logger umum
   - `rental.penyewaan` - Khusus operasi penyewaan
   - `rental.pembayaran` - Khusus operasi pembayaran

2. **Jalankan `cek_penyewaan` secara berkala** untuk mendeteksi keterlambatan

3. **Monitor file log** secara berkala untuk mendeteksi masalah

4. **Backup log files** sebelum dihapus otomatis oleh rotating handler

5. **Jangan simpan data sensitif** di log (password, token, dll)
