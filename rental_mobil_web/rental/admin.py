from django.contrib import admin
from django.utils.html import format_html
from .models import Mobil, Pelanggan, Penyewaan, Pembayaran, Notifikasi, LogAktivitas


@admin.register(Mobil)
class MobilAdmin(admin.ModelAdmin):
    list_display = ('id', 'merk', 'model', 'tahun', 'plat_nomor', 'harga_sewa_per_hari', 'status_badge')
    list_filter = ('status', 'merk', 'tahun')
    search_fields = ('merk', 'model', 'plat_nomor')
    ordering = ('-id',)
    
    def status_badge(self, obj):
        colors = {
            'tersedia': 'green',
            'disewa': 'orange',
            'perbaikan': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Pelanggan)
class PelangganAdmin(admin.ModelAdmin):
    list_display = ('id', 'nik', 'nama', 'no_telepon', 'email')
    search_fields = ('nik', 'nama', 'no_telepon', 'email')
    ordering = ('-id',)


@admin.register(Penyewaan)
class PenyewaanAdmin(admin.ModelAdmin):
    list_display = ('kode_penyewaan', 'pelanggan', 'mobil', 'tanggal_sewa', 'tanggal_kembali', 'total_biaya', 'status_badge')
    list_filter = ('status', 'tanggal_sewa')
    search_fields = ('kode_penyewaan', 'pelanggan__nama', 'mobil__plat_nomor')
    ordering = ('-id',)
    date_hierarchy = 'tanggal_sewa'
    
    def status_badge(self, obj):
        colors = {
            'aktif': 'blue',
            'selesai': 'green',
            'terlambat': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Pembayaran)
class PembayaranAdmin(admin.ModelAdmin):
    list_display = ('id', 'penyewaan', 'jumlah', 'metode_pembayaran', 'status_badge', 'created_at')
    list_filter = ('status', 'metode_pembayaran')
    search_fields = ('penyewaan__kode_penyewaan',)
    ordering = ('-id',)
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'lunas': 'green',
            'gagal': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Notifikasi)
class NotifikasiAdmin(admin.ModelAdmin):
    list_display = ('id', 'judul', 'tipe_badge', 'kategori', 'pelanggan_nama', 'dibaca_icon', 'dikirim_email_icon', 'created_at')
    list_filter = ('tipe', 'kategori', 'dibaca', 'dikirim_email')
    search_fields = ('judul', 'pesan', 'pelanggan_nama')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    actions = ['tandai_dibaca', 'tandai_belum_dibaca']
    
    def tipe_badge(self, obj):
        colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'success': '#28a745',
            'error': '#dc3545'
        }
        color = colors.get(obj.tipe, 'gray')
        text_color = 'black' if obj.tipe == 'warning' else 'white'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, text_color, obj.get_tipe_display()
        )
    tipe_badge.short_description = 'Tipe'
    
    def dibaca_icon(self, obj):
        if obj.dibaca:
            return format_html('<span style="color: green;">✓ Dibaca</span>')
        return format_html('<span style="color: red;">✗ Belum</span>')
    dibaca_icon.short_description = 'Dibaca'
    
    def dikirim_email_icon(self, obj):
        if obj.dikirim_email:
            return format_html('<span style="color: green;">✓ Terkirim</span>')
        return format_html('<span style="color: gray;">-</span>')
    dikirim_email_icon.short_description = 'Email'
    
    @admin.action(description='Tandai sebagai sudah dibaca')
    def tandai_dibaca(self, request, queryset):
        updated = queryset.update(dibaca=True)
        self.message_user(request, f'{updated} notifikasi ditandai sebagai sudah dibaca.')
    
    @admin.action(description='Tandai sebagai belum dibaca')
    def tandai_belum_dibaca(self, request, queryset):
        updated = queryset.update(dibaca=False)
        self.message_user(request, f'{updated} notifikasi ditandai sebagai belum dibaca.')


@admin.register(LogAktivitas)
class LogAktivitasAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'user', 'aksi_badge', 'model_name', 'object_repr', 'ip_address')
    list_filter = ('aksi', 'model_name')
    search_fields = ('user', 'model_name', 'object_repr', 'perubahan', 'ip_address')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'aksi', 'model_name', 'object_id', 'object_repr', 'perubahan', 'ip_address', 'user_agent', 'created_at')
    
    def aksi_badge(self, obj):
        colors = {
            'create': '#28a745',
            'update': '#17a2b8',
            'delete': '#dc3545',
            'view': '#6c757d',
            'login': '#007bff',
            'logout': '#ffc107'
        }
        color = colors.get(obj.aksi, 'gray')
        text_color = 'black' if obj.aksi == 'logout' else 'white'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, text_color, obj.get_aksi_display()
        )
    aksi_badge.short_description = 'Aksi'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Hanya superuser yang bisa hapus log
        return request.user.is_superuser

