"""
Management command untuk mengirim notifikasi reminder dan mengecek keterlambatan
Jalankan dengan: python manage.py cek_penyewaan
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rental.models import Penyewaan
from rental.services import NotifikasiService
import logging

logger = logging.getLogger('rental.penyewaan')


class Command(BaseCommand):
    help = 'Cek penyewaan untuk reminder dan keterlambatan'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reminder-days',
            type=int,
            default=1,
            help='Kirim reminder berapa hari sebelum tanggal kembali (default: 1)'
        )
    
    def handle(self, *args, **options):
        reminder_days = options['reminder_days']
        today = timezone.now().date()
        
        self.stdout.write(self.style.NOTICE(f'Mengecek penyewaan aktif pada {today}...'))
        
        # Cek penyewaan yang akan jatuh tempo
        reminder_date = today + timedelta(days=reminder_days)
        penyewaan_reminder = Penyewaan.objects.filter(
            status='aktif',
            tanggal_kembali=reminder_date
        )
        
        reminder_count = 0
        for penyewaan in penyewaan_reminder:
            try:
                NotifikasiService.notifikasi_reminder_pengembalian(penyewaan, reminder_days)
                reminder_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  Reminder terkirim: {penyewaan.kode_penyewaan}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Gagal kirim reminder {penyewaan.kode_penyewaan}: {e}')
                )
        
        # Cek penyewaan yang terlambat
        penyewaan_terlambat = Penyewaan.objects.filter(
            status='aktif',
            tanggal_kembali__lt=today
        )
        
        terlambat_count = 0
        for penyewaan in penyewaan_terlambat:
            try:
                hari_terlambat = (today - penyewaan.tanggal_kembali).days
                estimasi_denda = penyewaan.hitung_denda(hari_terlambat)
                
                # Update status menjadi terlambat
                penyewaan.status = 'terlambat'
                penyewaan.save()
                
                NotifikasiService.notifikasi_keterlambatan(
                    penyewaan, hari_terlambat, estimasi_denda
                )
                terlambat_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'  Keterlambatan: {penyewaan.kode_penyewaan} - '
                        f'{hari_terlambat} hari - Denda: Rp {estimasi_denda:,.0f}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Gagal proses {penyewaan.kode_penyewaan}: {e}')
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Selesai!'))
        self.stdout.write(f'  - Reminder terkirim: {reminder_count}')
        self.stdout.write(f'  - Penyewaan terlambat: {terlambat_count}')
        
        logger.info(
            f'Cek penyewaan selesai - Reminder: {reminder_count}, Terlambat: {terlambat_count}'
        )
