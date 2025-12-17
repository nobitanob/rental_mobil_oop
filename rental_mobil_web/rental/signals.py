"""
Django Signals untuk logging dan notifikasi otomatis
Dengan fitur tracking perubahan field (before/after)
"""
import logging
import json
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .models import Mobil, Pelanggan, Penyewaan, Pembayaran, LogAktivitas
from .services import NotifikasiService
from .log_aktivitas_service import LogAktivitasService
from .middleware import get_current_username, get_client_ip as get_middleware_client_ip, get_user_agent

logger = logging.getLogger('rental')
penyewaan_logger = logging.getLogger('rental.penyewaan')
pembayaran_logger = logging.getLogger('rental.pembayaran')


def create_log_with_user(aksi, model_name, object_id, object_repr, perubahan):
    """Helper untuk membuat log aktivitas dengan user info"""
    LogAktivitas.objects.create(
        user=get_current_username(),
        aksi=aksi,
        model_name=model_name,
        object_id=object_id,
        object_repr=object_repr,
        perubahan=perubahan,
        ip_address=get_middleware_client_ip(),
        user_agent=get_user_agent()
    )


# ==================== PRE-SAVE SIGNALS (untuk tracking perubahan) ====================

@receiver(pre_save, sender=Mobil)
def cache_mobil_pre_save(sender, instance, **kwargs):
    """Cache data mobil sebelum disimpan untuk tracking perubahan"""
    LogAktivitasService.cache_pre_save_data(instance)


@receiver(pre_save, sender=Pelanggan)
def cache_pelanggan_pre_save(sender, instance, **kwargs):
    """Cache data pelanggan sebelum disimpan untuk tracking perubahan"""
    LogAktivitasService.cache_pre_save_data(instance)


@receiver(pre_save, sender=Penyewaan)
def cache_penyewaan_pre_save(sender, instance, **kwargs):
    """Cache data penyewaan sebelum disimpan untuk tracking perubahan"""
    LogAktivitasService.cache_pre_save_data(instance)


@receiver(pre_save, sender=Pembayaran)
def cache_pembayaran_pre_save(sender, instance, **kwargs):
    """Cache data pembayaran sebelum disimpan untuk tracking perubahan"""
    LogAktivitasService.cache_pre_save_data(instance)


# ==================== LOGGING SIGNALS ====================

@receiver(post_save, sender=Mobil)
def log_mobil_save(sender, instance, created, **kwargs):
    """Log saat mobil dibuat atau diupdate dengan detail perubahan"""
    aksi = 'create' if created else 'update'
    aksi_text = 'ditambahkan' if created else 'diupdate'
    
    logger.info(f"Mobil {aksi_text}: {instance.merk} {instance.model} - {instance.plat_nomor}")
    
    # Dapatkan perubahan field jika update
    if not created:
        changes = LogAktivitasService.get_field_changes(instance)
        perubahan = LogAktivitasService.format_changes(changes) if changes else f"Status: {instance.status}"
    else:
        perubahan = f"Mobil baru: {instance.merk} {instance.model}, Plat: {instance.plat_nomor}, Harga: Rp {instance.harga_sewa_per_hari:,.0f}"
    
    create_log_with_user(aksi, 'Mobil', instance.id, str(instance), perubahan)


@receiver(post_delete, sender=Mobil)
def log_mobil_delete(sender, instance, **kwargs):
    """Log saat mobil dihapus dengan backup data"""
    logger.info(f"Mobil dihapus: {instance.merk} {instance.model} - {instance.plat_nomor}")
    
    # Backup data yang dihapus
    data_backup = {
        'merk': instance.merk,
        'model': instance.model,
        'tahun': instance.tahun,
        'plat_nomor': instance.plat_nomor,
        'harga_sewa_per_hari': str(instance.harga_sewa_per_hari),
        'status': instance.status
    }
    
    create_log_with_user('delete', 'Mobil', instance.id, str(instance),
        f"Data dihapus: {json.dumps(data_backup, ensure_ascii=False)}")


@receiver(post_save, sender=Pelanggan)
def log_pelanggan_save(sender, instance, created, **kwargs):
    """Log saat pelanggan dibuat atau diupdate dengan detail perubahan"""
    aksi = 'create' if created else 'update'
    aksi_text = 'ditambahkan' if created else 'diupdate'
    
    logger.info(f"Pelanggan {aksi_text}: {instance.nama} - NIK: {instance.nik}")
    
    # Dapatkan perubahan field jika update
    if not created:
        changes = LogAktivitasService.get_field_changes(instance)
        perubahan = LogAktivitasService.format_changes(changes) if changes else "Data pelanggan diupdate"
    else:
        perubahan = f"Pelanggan baru: {instance.nama}, NIK: {instance.nik}, Telp: {instance.no_telepon}"
    
    create_log_with_user(aksi, 'Pelanggan', instance.id, str(instance), perubahan)


@receiver(post_delete, sender=Pelanggan)
def log_pelanggan_delete(sender, instance, **kwargs):
    """Log saat pelanggan dihapus dengan backup data"""
    logger.info(f"Pelanggan dihapus: {instance.nama} - NIK: {instance.nik}")
    
    # Backup data yang dihapus
    data_backup = {
        'nik': instance.nik,
        'nama': instance.nama,
        'alamat': instance.alamat,
        'no_telepon': instance.no_telepon,
        'email': instance.email
    }
    
    create_log_with_user('delete', 'Pelanggan', instance.id, str(instance),
        f"Data dihapus: {json.dumps(data_backup, ensure_ascii=False)}")


@receiver(post_save, sender=Penyewaan)
def log_penyewaan_save(sender, instance, created, **kwargs):
    """Log dan notifikasi saat penyewaan dibuat atau diupdate dengan detail perubahan"""
    if created:
        penyewaan_logger.info(
            f"Penyewaan baru: {instance.kode_penyewaan} - "
            f"Pelanggan: {instance.pelanggan.nama} - "
            f"Mobil: {instance.mobil}"
        )
        
        perubahan = (
            f"Penyewaan baru: {instance.kode_penyewaan}\n"
            f"Pelanggan: {instance.pelanggan.nama}\n"
            f"Mobil: {instance.mobil}\n"
            f"Tanggal Sewa: {instance.tanggal_sewa}\n"
            f"Tanggal Kembali: {instance.tanggal_kembali}\n"
            f"Total Hari: {instance.total_hari}\n"
            f"Total Biaya: Rp {instance.total_biaya:,.0f}"
        )
        
        # Buat notifikasi penyewaan baru
        try:
            NotifikasiService.notifikasi_penyewaan_baru(instance)
        except Exception as e:
            logger.error(f"Gagal membuat notifikasi penyewaan: {str(e)}")
    else:
        # Dapatkan perubahan field
        changes = LogAktivitasService.get_field_changes(instance)
        perubahan = LogAktivitasService.format_changes(changes) if changes else f"Status: {instance.status}, Total: {instance.total_biaya}"
        
        penyewaan_logger.info(
            f"Penyewaan diupdate: {instance.kode_penyewaan} - "
            f"Status: {instance.status}"
        )
        
        # Jika status berubah menjadi selesai, buat notifikasi pengembalian
        if instance.status == 'selesai' and instance.tanggal_pengembalian:
            try:
                NotifikasiService.notifikasi_pengembalian(instance, instance.denda)
            except Exception as e:
                logger.error(f"Gagal membuat notifikasi pengembalian: {str(e)}")
    
    create_log_with_user('create' if created else 'update', 'Penyewaan', instance.id, str(instance), perubahan)


@receiver(post_delete, sender=Penyewaan)
def log_penyewaan_delete(sender, instance, **kwargs):
    """Log saat penyewaan dihapus dengan backup data"""
    penyewaan_logger.warning(f"Penyewaan dihapus: {instance.kode_penyewaan}")
    
    # Backup data yang dihapus
    data_backup = {
        'kode_penyewaan': instance.kode_penyewaan,
        'mobil': str(instance.mobil),
        'pelanggan': str(instance.pelanggan),
        'tanggal_sewa': str(instance.tanggal_sewa),
        'tanggal_kembali': str(instance.tanggal_kembali),
        'total_hari': instance.total_hari,
        'total_biaya': str(instance.total_biaya),
        'denda': str(instance.denda),
        'status': instance.status
    }
    
    create_log_with_user('delete', 'Penyewaan', instance.id, str(instance),
        f"Data dihapus: {json.dumps(data_backup, ensure_ascii=False)}")


@receiver(post_save, sender=Pembayaran)
def log_pembayaran_save(sender, instance, created, **kwargs):
    """Log dan notifikasi saat pembayaran dibuat atau diupdate dengan detail perubahan"""
    if created:
        pembayaran_logger.info(
            f"Pembayaran baru: Penyewaan {instance.penyewaan.kode_penyewaan} - "
            f"Jumlah: Rp {instance.jumlah:,.0f} - "
            f"Metode: {instance.metode_pembayaran}"
        )
        
        perubahan = (
            f"Pembayaran baru:\n"
            f"Penyewaan: {instance.penyewaan.kode_penyewaan}\n"
            f"Jumlah: Rp {instance.jumlah:,.0f}\n"
            f"Metode: {instance.get_metode_pembayaran_display()}\n"
            f"Status: {instance.get_status_display()}"
        )
        
        # Buat notifikasi pembayaran
        try:
            NotifikasiService.notifikasi_pembayaran(
                instance.penyewaan,
                float(instance.jumlah),
                instance.get_metode_pembayaran_display()
            )
        except Exception as e:
            logger.error(f"Gagal membuat notifikasi pembayaran: {str(e)}")
    else:
        # Dapatkan perubahan field
        changes = LogAktivitasService.get_field_changes(instance)
        perubahan = LogAktivitasService.format_changes(changes) if changes else f"Jumlah: {instance.jumlah}, Status: {instance.status}"
        
        pembayaran_logger.info(
            f"Pembayaran diupdate: Penyewaan {instance.penyewaan.kode_penyewaan} - "
            f"Status: {instance.status}"
        )
    
    create_log_with_user('create' if created else 'update', 'Pembayaran', instance.id, str(instance), perubahan)


@receiver(post_delete, sender=Pembayaran)
def log_pembayaran_delete(sender, instance, **kwargs):
    """Log saat pembayaran dihapus dengan backup data"""
    pembayaran_logger.warning(
        f"Pembayaran dihapus: Penyewaan {instance.penyewaan.kode_penyewaan}"
    )
    
    # Backup data yang dihapus
    data_backup = {
        'penyewaan': str(instance.penyewaan.kode_penyewaan),
        'jumlah': str(instance.jumlah),
        'metode_pembayaran': instance.metode_pembayaran,
        'status': instance.status,
        'bukti_pembayaran': instance.bukti_pembayaran
    }
    
    create_log_with_user('delete', 'Pembayaran', instance.id, str(instance),
        f"Data dihapus: {json.dumps(data_backup, ensure_ascii=False)}")


# ==================== AUTH SIGNALS ====================

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log saat user login"""
    ip = get_client_ip(request) if request else 'unknown'
    logger.info(f"User login: {user.username} - IP: {ip}")
    
    LogAktivitas.objects.create(
        user=user.username,
        aksi='login',
        model_name='User',
        object_id=user.id,
        object_repr=str(user),
        ip_address=ip,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else ''
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log saat user logout"""
    if user:
        ip = get_client_ip(request) if request else 'unknown'
        logger.info(f"User logout: {user.username} - IP: {ip}")
        
        LogAktivitas.objects.create(
            user=user.username,
            aksi='logout',
            model_name='User',
            object_id=user.id,
            object_repr=str(user),
            ip_address=ip
        )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log saat login gagal"""
    ip = get_client_ip(request) if request else 'unknown'
    username = credentials.get('username', 'unknown')
    
    logger.warning(f"Login gagal: {username} - IP: {ip}")
    
    LogAktivitas.objects.create(
        user=username,
        aksi='login',
        model_name='User',
        object_repr=f"Login gagal: {username}",
        ip_address=ip,
        perubahan="Login attempt failed"
    )


def get_client_ip(request):
    """Mendapatkan IP address client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
