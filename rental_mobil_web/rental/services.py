"""
Services untuk Notifikasi
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Notifikasi, Penyewaan, Pelanggan

logger = logging.getLogger('rental.notifikasi')


class NotifikasiService:
    """Service untuk mengelola notifikasi"""
    
    @staticmethod
    def buat_notifikasi(
        judul: str,
        pesan: str,
        tipe: str = 'info',
        kategori: str = 'sistem',
        penyewaan: Penyewaan = None,
        pelanggan: Pelanggan = None,
        kirim_email: bool = False
    ) -> Notifikasi:
        """
        Membuat notifikasi baru
        
        Args:
            judul: Judul notifikasi
            pesan: Isi pesan notifikasi
            tipe: Tipe notifikasi (info, warning, success, error)
            kategori: Kategori notifikasi
            penyewaan: Instance Penyewaan terkait (optional)
            pelanggan: Instance Pelanggan terkait (optional)
            kirim_email: Apakah mengirim email (default False)
        
        Returns:
            Instance Notifikasi yang dibuat
        """
        try:
            notifikasi = Notifikasi.objects.create(
                judul=judul,
                pesan=pesan,
                tipe=tipe,
                kategori=kategori,
                penyewaan_id_ref=penyewaan.id if penyewaan else None,
                pelanggan_id_ref=pelanggan.id if pelanggan else None,
                pelanggan_nama=pelanggan.nama if pelanggan else '',
                dikirim_email=False
            )
            
            logger.info(f"Notifikasi dibuat: {judul} - Kategori: {kategori}")
            
            # Kirim email jika diminta
            if kirim_email and pelanggan and pelanggan.email:
                email_terkirim = NotifikasiService.kirim_email_notifikasi(
                    notifikasi, pelanggan.email
                )
                if email_terkirim:
                    notifikasi.dikirim_email = True
                    notifikasi.save()
            
            return notifikasi
            
        except Exception as e:
            logger.error(f"Gagal membuat notifikasi: {str(e)}")
            raise
    
    @staticmethod
    def kirim_email_notifikasi(notifikasi: Notifikasi, email_tujuan: str) -> bool:
        """
        Mengirim notifikasi via email
        
        Args:
            notifikasi: Instance Notifikasi
            email_tujuan: Alamat email tujuan
        
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            subject = f"[Rental Mobil] {notifikasi.judul}"
            
            # HTML message
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #333;">{notifikasi.judul}</h2>
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                        <p>{notifikasi.pesan}</p>
                    </div>
                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Email ini dikirim secara otomatis oleh sistem Rental Mobil.
                        Mohon tidak membalas email ini.
                    </p>
                </div>
            </body>
            </html>
            """
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_tujuan],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Email notifikasi terkirim ke: {email_tujuan}")
            return True
            
        except Exception as e:
            logger.error(f"Gagal mengirim email ke {email_tujuan}: {str(e)}")
            return False
    
    @staticmethod
    def notifikasi_penyewaan_baru(penyewaan: Penyewaan) -> Notifikasi:
        """Buat notifikasi untuk penyewaan baru"""
        judul = f"Penyewaan Baru - {penyewaan.kode_penyewaan}"
        pesan = (
            f"Penyewaan baru telah dibuat:\n\n"
            f"Kode: {penyewaan.kode_penyewaan}\n"
            f"Pelanggan: {penyewaan.pelanggan.nama}\n"
            f"Mobil: {penyewaan.mobil}\n"
            f"Tanggal Sewa: {penyewaan.tanggal_sewa}\n"
            f"Tanggal Kembali: {penyewaan.tanggal_kembali}\n"
            f"Total Biaya: Rp {penyewaan.total_biaya:,.0f}"
        )
        
        return NotifikasiService.buat_notifikasi(
            judul=judul,
            pesan=pesan,
            tipe='success',
            kategori='penyewaan_baru',
            penyewaan=penyewaan,
            pelanggan=penyewaan.pelanggan,
            kirim_email=True
        )
    
    @staticmethod
    def notifikasi_pembayaran(penyewaan: Penyewaan, jumlah: float, metode: str) -> Notifikasi:
        """Buat notifikasi untuk pembayaran"""
        judul = f"Pembayaran Diterima - {penyewaan.kode_penyewaan}"
        pesan = (
            f"Pembayaran telah diterima:\n\n"
            f"Kode Penyewaan: {penyewaan.kode_penyewaan}\n"
            f"Jumlah: Rp {jumlah:,.0f}\n"
            f"Metode: {metode}"
        )
        
        return NotifikasiService.buat_notifikasi(
            judul=judul,
            pesan=pesan,
            tipe='success',
            kategori='pembayaran',
            penyewaan=penyewaan,
            pelanggan=penyewaan.pelanggan,
            kirim_email=True
        )
    
    @staticmethod
    def notifikasi_pengembalian(penyewaan: Penyewaan, denda: float = 0) -> Notifikasi:
        """Buat notifikasi untuk pengembalian mobil"""
        if denda > 0:
            judul = f"Pengembalian dengan Denda - {penyewaan.kode_penyewaan}"
            tipe = 'warning'
            pesan = (
                f"Mobil telah dikembalikan dengan denda keterlambatan:\n\n"
                f"Kode Penyewaan: {penyewaan.kode_penyewaan}\n"
                f"Mobil: {penyewaan.mobil}\n"
                f"Denda: Rp {denda:,.0f}"
            )
        else:
            judul = f"Pengembalian Sukses - {penyewaan.kode_penyewaan}"
            tipe = 'success'
            pesan = (
                f"Mobil telah dikembalikan dengan sukses:\n\n"
                f"Kode Penyewaan: {penyewaan.kode_penyewaan}\n"
                f"Mobil: {penyewaan.mobil}"
            )
        
        return NotifikasiService.buat_notifikasi(
            judul=judul,
            pesan=pesan,
            tipe=tipe,
            kategori='pengembalian',
            penyewaan=penyewaan,
            pelanggan=penyewaan.pelanggan,
            kirim_email=True
        )
    
    @staticmethod
    def notifikasi_reminder_pengembalian(penyewaan: Penyewaan, hari_tersisa: int) -> Notifikasi:
        """Buat notifikasi reminder pengembalian"""
        judul = f"Reminder: Pengembalian {hari_tersisa} Hari Lagi"
        pesan = (
            f"Pengingat pengembalian mobil:\n\n"
            f"Kode Penyewaan: {penyewaan.kode_penyewaan}\n"
            f"Mobil: {penyewaan.mobil}\n"
            f"Tanggal Kembali: {penyewaan.tanggal_kembali}\n\n"
            f"Mohon kembalikan mobil tepat waktu untuk menghindari denda."
        )
        
        return NotifikasiService.buat_notifikasi(
            judul=judul,
            pesan=pesan,
            tipe='info',
            kategori='reminder',
            penyewaan=penyewaan,
            pelanggan=penyewaan.pelanggan,
            kirim_email=True
        )
    
    @staticmethod
    def notifikasi_keterlambatan(penyewaan: Penyewaan, hari_terlambat: int, estimasi_denda: float) -> Notifikasi:
        """Buat notifikasi keterlambatan"""
        judul = f"PERINGATAN: Keterlambatan {hari_terlambat} Hari"
        pesan = (
            f"Mobil belum dikembalikan dan sudah terlambat:\n\n"
            f"Kode Penyewaan: {penyewaan.kode_penyewaan}\n"
            f"Mobil: {penyewaan.mobil}\n"
            f"Tanggal Seharusnya Kembali: {penyewaan.tanggal_kembali}\n"
            f"Keterlambatan: {hari_terlambat} hari\n"
            f"Estimasi Denda: Rp {estimasi_denda:,.0f}\n\n"
            f"Segera kembalikan mobil untuk menghindari denda lebih besar."
        )
        
        return NotifikasiService.buat_notifikasi(
            judul=judul,
            pesan=pesan,
            tipe='error',
            kategori='keterlambatan',
            penyewaan=penyewaan,
            pelanggan=penyewaan.pelanggan,
            kirim_email=True
        )
    
    @staticmethod
    def get_notifikasi_belum_dibaca(limit: int = 10) -> list:
        """Mendapatkan notifikasi yang belum dibaca"""
        return Notifikasi.objects.filter(dibaca=False)[:limit]
    
    @staticmethod
    def get_jumlah_notifikasi_belum_dibaca() -> int:
        """Mendapatkan jumlah notifikasi yang belum dibaca"""
        return Notifikasi.objects.filter(dibaca=False).count()
    
    @staticmethod
    def tandai_semua_dibaca():
        """Tandai semua notifikasi sebagai sudah dibaca"""
        Notifikasi.objects.filter(dibaca=False).update(dibaca=True)
        logger.info("Semua notifikasi ditandai sebagai sudah dibaca")
