"""Demo Log Aktivitas dengan User/Pelanggan"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_mobil_web.settings')
django.setup()

from rental.models import Mobil, Pelanggan, Penyewaan, LogAktivitas
from datetime import date, timedelta
import random

print('=' * 70)
print('  DEMO: Log Aktivitas dengan User yang Tercatat')
print('=' * 70)

# Buat pelanggan baru dengan NIK random
nik = f'320{random.randint(1000000000000, 9999999999999)}'
print('\n[1] CREATE PELANGGAN')
print('-' * 50)
pelanggan = Pelanggan.objects.create(
    nik=nik,
    nama='Dewi Lestari',
    alamat='Jl. Sudirman No. 456, Bandung',
    no_telepon='082345678901',
    email='dewi.lestari@email.com'
)
print(f'   Pelanggan dibuat: {pelanggan.nama}')
print(f'   NIK: {pelanggan.nik}')

# Cek log
log = LogAktivitas.objects.filter(model_name='Pelanggan', object_id=pelanggan.id).first()
if log:
    print(f'   LOG: User={log.user}, Aksi={log.aksi}, IP={log.ip_address}')

# Buat penyewaan baru
print('\n[2] CREATE PENYEWAAN')
print('-' * 50)
mobil = Mobil.objects.filter(status='tersedia').first()
if mobil:
    penyewaan = Penyewaan.objects.create(
        mobil=mobil,
        pelanggan=pelanggan,
        tanggal_sewa=date.today(),
        tanggal_kembali=date.today() + timedelta(days=3),
        total_hari=3,
        total_biaya=mobil.harga_sewa_per_hari * 3,
        status='aktif'
    )
    print(f'   Penyewaan dibuat: {penyewaan.kode_penyewaan}')
    print(f'   Mobil: {mobil.merk} {mobil.model}')
    print(f'   Pelanggan: {pelanggan.nama}')
    
    # Cek log
    log = LogAktivitas.objects.filter(model_name='Penyewaan', object_id=penyewaan.id).first()
    if log:
        print(f'   LOG: User={log.user}, Aksi={log.aksi}')

# Update mobil
print('\n[3] UPDATE MOBIL')
print('-' * 50)
mobil2 = Mobil.objects.get(id=19)
old_price = mobil2.harga_sewa_per_hari
mobil2.harga_sewa_per_hari = 600000
mobil2.save()
print(f'   Mobil diupdate: {mobil2.merk} {mobil2.model}')
print(f'   Harga: {old_price} -> {mobil2.harga_sewa_per_hari}')

# Tampilkan Log Aktivitas terbaru
print('\n[4] LOG AKTIVITAS TERBARU')
print('-' * 50)
print(f'{"User":<15} {"Aksi":<8} {"Model":<12} {"Object":<30} {"IP":<15}')
print('-' * 80)

logs = LogAktivitas.objects.all().order_by('-created_at')[:10]
for log in logs:
    obj = log.object_repr[:28] + '..' if len(log.object_repr) > 30 else log.object_repr
    ip = log.ip_address or '-'
    print(f'{log.user:<15} {log.aksi:<8} {log.model_name:<12} {obj:<30} {ip:<15}')

print('\n' + '=' * 70)
print('  User tercatat di setiap aktivitas!')
print('  Lihat di Django Admin: /admin/rental/logaktivitas/')
print('=' * 70)
