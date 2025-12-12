"""
Django Signals untuk logging dan notifikasi otomatis
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .models import Mobil, Pelanggan, Penyewaan, Pembayaran, LogAktivitas
from .services import NotifikasiService

logger = logging.getLogger('rental')
penyewaan_logger = logging.getLogger('rental.penyewaan')
pembayaran_logger = logging.getLogger('rental.pembayaran')


# ==================== LOGGING SIGNALS ====================

@receiver(post_save, sender=Mobil)
def log_mobil_save(sender, instance, created, **kwargs):
    """Log saat mobil dibuat atau diupdate"""
    aksi = 'create' if created else 'update'
    aksi_text = 'ditambahkan' if created else 'diupdate'
    
    logger.info(f"Mobil {aksi_text}: {instance.merk} {instance.model} - {instance.plat_nomor}")
    
    LogAktivitas.objects.create(
        aksi=aksi,
        model_name='Mobil',
        object_id=instance.id,
        object_repr=str(instance),
        perubahan=f"Status: {instance.status}"
    )


@receiver(post_delete, sender=Mobil)
def log_mobil_delete(sender, instance, **kwargs):
    """Log saat mobil dihapus"""
    logger.info(f"Mobil dihapus: {instance.merk} {instance.model} - {instance.plat_nomor}")
    
    LogAktivitas.objects.create(
        aksi='delete',
        model_name='Mobil',
        object_id=instance.id,
        object_repr=str(instance)
    )


@receiver(post_save, sender=Pelanggan)
def log_pelanggan_save(sender, instance, created, **kwargs):
    """Log saat pelanggan dibuat atau diupdate"""
    aksi = 'create' if created else 'update'
    aksi_text = 'ditambahkan' if created else 'diupdate'
    
    logger.info(f"Pelanggan {aksi_text}: {instance.nama} - NIK: {instance.nik}")
    
    LogAktivitas.objects.create(
        aksi=aksi,
        model_name='Pelanggan',
        object_id=instance.id,
        object_repr=str(instance)
    )


@receiver(post_delete, sender=Pelanggan)
def log_pelanggan_delete(sender, instance, **kwargs):
    """Log saat pelanggan dihapus"""
    logger.info(f"Pelanggan dihapus: {instance.nama} - NIK: {instance.nik}")
    
    LogAktivitas.objects.create(
        aksi='delete',
        model_name='Pelanggan',
        object_id=instance.id,
        object_repr=str(instance)
    )


@receiver(post_save, sender=Penyewaan)
def log_penyewaan_save(sender, instance, created, **kwargs):
    """Log dan notifikasi saat penyewaan dibuat atau diupdate"""
    if created:
        penyewaan_logger.info(
            f"Penyewaan baru: {instance.kode_penyewaan} - "
            f"Pelanggan: {instance.pelanggan.nama} - "
            f"Mobil: {instance.mobil}"
        )
        
        # Buat notifikasi penyewaan baru
        try:
            NotifikasiService.notifikasi_penyewaan_baru(instance)
        except Exception as e:
            logger.error(f"Gagal membuat notifikasi penyewaan: {str(e)}")
    else:
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
    
    LogAktivitas.objects.create(
        aksi='create' if created else 'update',
        model_name='Penyewaan',
        object_id=instance.id,
        object_repr=str(instance),
        perubahan=f"Status: {instance.status}, Total: {instance.total_biaya}"
    )


@receiver(post_delete, sender=Penyewaan)
def log_penyewaan_delete(sender, instance, **kwargs):
    """Log saat penyewaan dihapus"""
    penyewaan_logger.warning(f"Penyewaan dihapus: {instance.kode_penyewaan}")
    
    LogAktivitas.objects.create(
        aksi='delete',
        model_name='Penyewaan',
        object_id=instance.id,
        object_repr=str(instance)
    )


@receiver(post_save, sender=Pembayaran)
def log_pembayaran_save(sender, instance, created, **kwargs):
    """Log dan notifikasi saat pembayaran dibuat atau diupdate"""
    if created:
        pembayaran_logger.info(
            f"Pembayaran baru: Penyewaan {instance.penyewaan.kode_penyewaan} - "
            f"Jumlah: Rp {instance.jumlah:,.0f} - "
            f"Metode: {instance.metode_pembayaran}"
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
        pembayaran_logger.info(
            f"Pembayaran diupdate: Penyewaan {instance.penyewaan.kode_penyewaan} - "
            f"Status: {instance.status}"
        )
    
    LogAktivitas.objects.create(
        aksi='create' if created else 'update',
        model_name='Pembayaran',
        object_id=instance.id,
        object_repr=str(instance),
        perubahan=f"Jumlah: {instance.jumlah}, Status: {instance.status}"
    )


@receiver(post_delete, sender=Pembayaran)
def log_pembayaran_delete(sender, instance, **kwargs):
    """Log saat pembayaran dihapus"""
    pembayaran_logger.warning(
        f"Pembayaran dihapus: Penyewaan {instance.penyewaan.kode_penyewaan}"
    )
    
    LogAktivitas.objects.create(
        aksi='delete',
        model_name='Pembayaran',
        object_id=instance.id,
        object_repr=str(instance)
    )


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
