from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, EmailValidator
from datetime import date


class Mobil(models.Model):
    """Model untuk Mobil"""
    
    STATUS_CHOICES = [
        ('tersedia', 'Tersedia'),
        ('disewa', 'Disewa'),
        ('perbaikan', 'Perbaikan'),
    ]
    
    merk = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    tahun = models.IntegerField(validators=[MinValueValidator(1900)])
    plat_nomor = models.CharField(
        max_length=15, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z]{1,2}\s?\d{1,4}\s?[A-Z]{1,3}$',
            message='Format plat nomor tidak valid (contoh: B 1234 ABC)'
        )]
    )
    harga_sewa_per_hari = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='tersedia')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mobil'
        verbose_name = 'Mobil'
        verbose_name_plural = 'Daftar Mobil'
        managed = False  # Karena tabel sudah ada dari CLI
    
    def __str__(self):
        return f"{self.merk} {self.model} ({self.tahun}) - {self.plat_nomor}"


class Pelanggan(models.Model):
    """Model untuk Pelanggan"""
    
    nik = models.CharField(
        max_length=16, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{16}$',
            message='NIK harus 16 digit angka'
        )]
    )
    nama = models.CharField(max_length=100)
    alamat = models.TextField(blank=True, default='')
    no_telepon = models.CharField(max_length=15, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pelanggan'
        verbose_name = 'Pelanggan'
        verbose_name_plural = 'Daftar Pelanggan'
        managed = False
    
    def __str__(self):
        return f"{self.nama} ({self.nik})"


class Penyewaan(models.Model):
    """Model untuk Penyewaan"""
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('selesai', 'Selesai'),
        ('terlambat', 'Terlambat'),
    ]
    
    kode_penyewaan = models.CharField(max_length=20, unique=True, blank=True)
    mobil = models.ForeignKey(Mobil, on_delete=models.CASCADE, related_name='penyewaan')
    pelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE, related_name='penyewaan')
    tanggal_sewa = models.DateField()
    tanggal_kembali = models.DateField()
    tanggal_pengembalian = models.DateField(null=True, blank=True)
    total_hari = models.IntegerField(validators=[MinValueValidator(1)])
    total_biaya = models.DecimalField(max_digits=15, decimal_places=2)
    denda = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'penyewaan'
        verbose_name = 'Penyewaan'
        verbose_name_plural = 'Daftar Penyewaan'
        managed = False
    
    def save(self, *args, **kwargs):
        if not self.kode_penyewaan:
            # Generate kode penyewaan
            today = date.today()
            prefix = f"RNT-{today.strftime('%Y%m%d')}"
            last = Penyewaan.objects.filter(kode_penyewaan__startswith=prefix).order_by('-id').first()
            if last:
                last_seq = int(last.kode_penyewaan.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            self.kode_penyewaan = f"{prefix}-{new_seq:04d}"
        super().save(*args, **kwargs)
    
    def hitung_denda(self, hari_keterlambatan: int) -> float:
        """Hitung denda berdasarkan keterlambatan (150% per hari)"""
        if hari_keterlambatan > 0:
            return float(self.mobil.harga_sewa_per_hari) * hari_keterlambatan * 1.5
        return 0
    
    def __str__(self):
        return f"{self.kode_penyewaan} - {self.pelanggan.nama}"


class Pembayaran(models.Model):
    """Model untuk Pembayaran"""
    
    METODE_CHOICES = [
        ('tunai', 'Tunai'),
        ('transfer', 'Transfer Bank'),
        ('kartu_kredit', 'Kartu Kredit'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('lunas', 'Lunas'),
        ('gagal', 'Gagal'),
    ]
    
    penyewaan = models.ForeignKey(Penyewaan, on_delete=models.CASCADE, related_name='pembayaran')
    jumlah = models.DecimalField(max_digits=15, decimal_places=2)
    metode_pembayaran = models.CharField(max_length=20, choices=METODE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bukti_pembayaran = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pembayaran'
        verbose_name = 'Pembayaran'
        verbose_name_plural = 'Daftar Pembayaran'
        managed = False
    
    def __str__(self):
        return f"Pembayaran {self.penyewaan.kode_penyewaan} - Rp {self.jumlah:,.0f}"


class Notifikasi(models.Model):
    """Model untuk Notifikasi"""
    
    TIPE_CHOICES = [
        ('info', 'Informasi'),
        ('warning', 'Peringatan'),
        ('success', 'Sukses'),
        ('error', 'Error'),
    ]
    
    KATEGORI_CHOICES = [
        ('penyewaan_baru', 'Penyewaan Baru'),
        ('pembayaran', 'Pembayaran'),
        ('pengembalian', 'Pengembalian'),
        ('keterlambatan', 'Keterlambatan'),
        ('reminder', 'Pengingat'),
        ('sistem', 'Sistem'),
    ]
    
    judul = models.CharField(max_length=200)
    pesan = models.TextField()
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, default='info')
    kategori = models.CharField(max_length=30, choices=KATEGORI_CHOICES, default='sistem')
    # Menggunakan integer untuk referensi karena tabel asli tidak dikelola Django
    penyewaan_id_ref = models.IntegerField(null=True, blank=True, verbose_name='ID Penyewaan')
    pelanggan_id_ref = models.IntegerField(null=True, blank=True, verbose_name='ID Pelanggan')
    pelanggan_nama = models.CharField(max_length=100, blank=True, default='', verbose_name='Nama Pelanggan')
    dibaca = models.BooleanField(default=False)
    dikirim_email = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifikasi'
        verbose_name = 'Notifikasi'
        verbose_name_plural = 'Daftar Notifikasi'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.get_tipe_display()}] {self.judul}"
    
    def tandai_dibaca(self):
        """Tandai notifikasi sebagai sudah dibaca"""
        self.dibaca = True
        self.save()
    
    def get_penyewaan(self):
        """Mendapatkan objek Penyewaan terkait"""
        if self.penyewaan_id_ref:
            try:
                return Penyewaan.objects.get(id=self.penyewaan_id_ref)
            except Penyewaan.DoesNotExist:
                return None
        return None
    
    def get_pelanggan(self):
        """Mendapatkan objek Pelanggan terkait"""
        if self.pelanggan_id_ref:
            try:
                return Pelanggan.objects.get(id=self.pelanggan_id_ref)
            except Pelanggan.DoesNotExist:
                return None
        return None


class LogAktivitas(models.Model):
    """Model untuk Log Aktivitas User"""
    
    AKSI_CHOICES = [
        ('create', 'Tambah'),
        ('update', 'Ubah'),
        ('delete', 'Hapus'),
        ('view', 'Lihat'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    user = models.CharField(max_length=100, blank=True, default='system')
    aksi = models.CharField(max_length=20, choices=AKSI_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.IntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=255, blank=True, default='')
    perubahan = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'log_aktivitas'
        verbose_name = 'Log Aktivitas'
        verbose_name_plural = 'Log Aktivitas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.created_at}] {self.user} - {self.get_aksi_display()} {self.model_name}"

