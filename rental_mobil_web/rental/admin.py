from django.contrib import admin
from .models import Mobil, Pelanggan, Penyewaan, Pembayaran


@admin.register(Mobil)
class MobilAdmin(admin.ModelAdmin):
    list_display = ('id', 'merk', 'model', 'tahun', 'plat_nomor', 'harga_sewa_per_hari', 'status')
    list_filter = ('status', 'merk', 'tahun')
    search_fields = ('merk', 'model', 'plat_nomor')
    ordering = ('-id',)


@admin.register(Pelanggan)
class PelangganAdmin(admin.ModelAdmin):
    list_display = ('id', 'nik', 'nama', 'no_telepon', 'email')
    search_fields = ('nik', 'nama', 'no_telepon', 'email')
    ordering = ('-id',)


@admin.register(Penyewaan)
class PenyewaanAdmin(admin.ModelAdmin):
    list_display = ('kode_penyewaan', 'pelanggan', 'mobil', 'tanggal_sewa', 'tanggal_kembali', 'total_biaya', 'status')
    list_filter = ('status', 'tanggal_sewa')
    search_fields = ('kode_penyewaan', 'pelanggan__nama', 'mobil__plat_nomor')
    ordering = ('-id',)
    date_hierarchy = 'tanggal_sewa'


@admin.register(Pembayaran)
class PembayaranAdmin(admin.ModelAdmin):
    list_display = ('id', 'penyewaan', 'jumlah', 'metode_pembayaran', 'status', 'created_at')
    list_filter = ('status', 'metode_pembayaran')
    search_fields = ('penyewaan__kode_penyewaan',)
    ordering = ('-id',)

