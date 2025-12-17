from django.contrib import admin
from django.utils.html import format_html
from .models import Mobil, Pelanggan, Penyewaan, Pembayaran, Notifikasi, LogAktivitas, DataVersion


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
    list_filter = ('aksi', 'model_name', 'user')
    search_fields = ('user', 'model_name', 'object_repr', 'perubahan', 'ip_address')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'aksi', 'model_name', 'object_id', 'object_repr', 'perubahan', 'ip_address', 'user_agent', 'created_at')
    list_per_page = 50
    date_hierarchy = 'created_at'
    actions = ['export_logs_json', 'hapus_log_lama']
    
    fieldsets = (
        ('Informasi Aktivitas', {
            'fields': ('aksi', 'model_name', 'object_id', 'object_repr')
        }),
        ('Detail Perubahan', {
            'fields': ('perubahan',),
            'classes': ('collapse',)
        }),
        ('Informasi User', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Waktu', {
            'fields': ('created_at',)
        }),
    )
    
    def aksi_badge(self, obj):
        colors = {
            'create': '#28a745',
            'update': '#17a2b8',
            'delete': '#dc3545',
            'view': '#6c757d',
            'login': '#007bff',
            'logout': '#ffc107'
        }
        icons = {
            'create': '➕',
            'update': '✏️',
            'delete': '🗑️',
            'view': '👁️',
            'login': '🔓',
            'logout': '🔒'
        }
        color = colors.get(obj.aksi, 'gray')
        icon = icons.get(obj.aksi, '•')
        text_color = 'black' if obj.aksi == 'logout' else 'white'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; border-radius: 3px;">{} {}</span>',
            color, text_color, icon, obj.get_aksi_display()
        )
    aksi_badge.short_description = 'Aksi'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow superuser to add notes
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        # Hanya superuser yang bisa hapus log
        return request.user.is_superuser
    
    @admin.action(description='📥 Export logs ke JSON')
    def export_logs_json(self, request, queryset):
        """Export selected logs ke JSON"""
        import json
        from django.http import HttpResponse
        
        data = []
        for log in queryset:
            data.append({
                'id': log.id,
                'user': log.user,
                'aksi': log.aksi,
                'model_name': log.model_name,
                'object_id': log.object_id,
                'object_repr': log.object_repr,
                'perubahan': log.perubahan,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat() if log.created_at else None
            })
        
        response = HttpResponse(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="log_aktivitas.json"'
        return response
    
    @admin.action(description='🗑️ Hapus log lebih dari 90 hari')
    def hapus_log_lama(self, request, queryset):
        """Hapus log yang lebih dari 90 hari"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=90)
        deleted, _ = LogAktivitas.objects.filter(created_at__lt=cutoff).delete()
        self.message_user(request, f'{deleted} log lama berhasil dihapus.')


@admin.register(DataVersion)
class DataVersionAdmin(admin.ModelAdmin):
    """Admin untuk Version Control Data"""
    list_display = ('id', 'model_name', 'object_id', 'version', 'action_badge', 'branch', 'created_by', 'commit_message_short', 'created_at')
    list_filter = ('model_name', 'action', 'branch', 'created_by')
    search_fields = ('model_name', 'object_id', 'commit_message', 'created_by')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('model_name', 'object_id', 'version', 'data_snapshot', 'action', 'created_by', 
                       'created_at', 'parent_version', 'branch', 'is_current', 'display_changes')
    
    fieldsets = (
        ('Informasi Versi', {
            'fields': ('model_name', 'object_id', 'version', 'branch', 'is_current')
        }),
        ('Aksi & User', {
            'fields': ('action', 'created_by', 'created_at', 'commit_message')
        }),
        ('Relasi', {
            'fields': ('parent_version',),
            'classes': ('collapse',)
        }),
        ('Data Snapshot', {
            'fields': ('data_snapshot', 'display_changes'),
            'classes': ('collapse',)
        }),
    )
    
    def action_badge(self, obj):
        icons = {
            'create': '➕',
            'update': '✏️',
            'delete': '🗑️',
            'commit': '📝',
            'rollback': '↩️',
        }
        colors = {
            'create': 'green',
            'update': 'blue',
            'delete': 'red',
            'commit': 'purple',
            'rollback': 'orange',
        }
        icon = icons.get(obj.action, '❓')
        color = colors.get(obj.action, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{} {}</span>',
            color, icon, obj.action.title()
        )
    action_badge.short_description = 'Aksi'
    
    def commit_message_short(self, obj):
        if obj.commit_message:
            return obj.commit_message[:50] + '...' if len(obj.commit_message) > 50 else obj.commit_message
        return '-'
    commit_message_short.short_description = 'Pesan Commit'
    
    def display_changes(self, obj):
        changes = obj.get_changes_from_parent()
        if not changes:
            return 'Tidak ada perubahan'
        
        html = '<table style="width:100%; border-collapse: collapse;">'
        html += '<tr style="background:#f0f0f0;"><th style="padding:5px;border:1px solid #ddd;">Field</th>'
        html += '<th style="padding:5px;border:1px solid #ddd;">Lama</th>'
        html += '<th style="padding:5px;border:1px solid #ddd;">Baru</th></tr>'
        
        for field, vals in changes.items():
            if isinstance(vals, dict) and 'old' in vals and 'new' in vals:
                html += f'<tr><td style="padding:5px;border:1px solid #ddd;"><strong>{field}</strong></td>'
                html += f'<td style="padding:5px;border:1px solid #ddd;color:red;">{vals["old"]}</td>'
                html += f'<td style="padding:5px;border:1px solid #ddd;color:green;">{vals["new"]}</td></tr>'
            else:
                html += f'<tr><td style="padding:5px;border:1px solid #ddd;" colspan="3">{field}: {vals}</td></tr>'
        
        html += '</table>'
        return format_html(html)
    display_changes.short_description = 'Perubahan dari Versi Sebelumnya'
    
    def has_add_permission(self, request):
        return False  # Tidak boleh tambah manual
    
    def has_change_permission(self, request, obj=None):
        return False  # Tidak boleh edit
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Hanya superuser boleh hapus
    
    actions = ['rollback_to_version']
    
    @admin.action(description='↩️ Rollback ke versi ini')
    def rollback_to_version(self, request, queryset):
        """Rollback data ke versi yang dipilih"""
        from .version_control import VersionControlService
        
        if queryset.count() != 1:
            self.message_user(request, 'Pilih tepat 1 versi untuk rollback!', level='error')
            return
        
        version = queryset.first()
        try:
            result = VersionControlService.rollback(
                model_name=version.model_name,
                object_id=version.object_id,
                version=version.version,
                user=request.user.username
            )
            if result:
                self.message_user(request, f'Berhasil rollback {version.model_name}#{version.object_id} ke versi {version.version}')
            else:
                self.message_user(request, 'Gagal rollback: objek tidak ditemukan', level='error')
        except Exception as e:
            self.message_user(request, f'Error: {str(e)}', level='error')

