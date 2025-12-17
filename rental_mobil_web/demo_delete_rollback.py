"""Demo DELETE lalu ROLLBACK"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_mobil_web.settings')
django.setup()

from rental.models import Mobil, DataVersion
from rental.version_control import VCS

print('=' * 70)
print('  DEMO: DELETE lalu ROLLBACK')
print('=' * 70)

# Ambil mobil
mobil = Mobil.objects.get(id=19)
mobil_id = mobil.id

print(f'\n[1] DATA SEBELUM DELETE')
print('-' * 50)
print(f'   ID: {mobil.id}')
print(f'   Merk/Model: {mobil.merk} {mobil.model}')
print(f'   Plat: {mobil.plat_nomor}')
print(f'   Harga: Rp {mobil.harga_sewa_per_hari:,.0f}')
print(f'   Status: {mobil.status}')

# STEP 1: Commit DELETE (backup data)
print('\n[2] COMMIT DELETE (Backup data)')
print('-' * 50)
VCS.commit_delete(mobil, 'Mobil dihapus untuk demo rollback', user='admin')
print('   Snapshot tersimpan di DataVersion')

# STEP 2: Delete dari database
mobil.delete()
print('\n[3] DELETE EXECUTED')
print('-' * 50)
print(f'   Mobil ID {mobil_id} DIHAPUS dari database!')

# Verifikasi delete
try:
    Mobil.objects.get(id=mobil_id)
    print('   ERROR: Masih ada!')
except Mobil.DoesNotExist:
    print('   Verifikasi: Data sudah tidak ada di database')

# STEP 3: ROLLBACK - Kembalikan data!
print('\n[4] ROLLBACK - Mengembalikan Data')
print('-' * 50)
print('   Menjalankan VCS.rollback()...')

result = VCS.rollback('Mobil', mobil_id, version=5, user='admin')

if result:
    print('\n   ROLLBACK BERHASIL!')
    print(f'   ID: {result.id}')
    print(f'   Merk/Model: {result.merk} {result.model}')
    print(f'   Plat: {result.plat_nomor}')
    print(f'   Harga: Rp {result.harga_sewa_per_hari:,.0f}')
    print(f'   Status: {result.status}')
else:
    print('   ROLLBACK GAGAL!')

# Verifikasi rollback
print('\n[5] VERIFIKASI - Cek Database')
print('-' * 50)
try:
    mobil_restored = Mobil.objects.get(id=mobil_id)
    print(f'   Data BERHASIL dikembalikan!')
    print(f'   {mobil_restored.merk} {mobil_restored.model} - {mobil_restored.plat_nomor}')
except Mobil.DoesNotExist:
    print('   Data tidak ditemukan')

# History
print('\n[6] VERSION HISTORY')
print('-' * 50)
history = VCS.get_history('Mobil', mobil_id)
for v in history:
    icons = {'create': '+', 'update': '~', 'delete': 'X', 'rollback': '<'}
    icon = icons.get(v.action, '*')
    current = ' [CURRENT]' if v.is_current else ''
    print(f'   v{v.version} [{icon}] {v.action.upper()}{current}')
    print(f'       {v.commit_message}')

print('\n' + '=' * 70)
print('  DATA YANG DIHAPUS BERHASIL DI-ROLLBACK!')
print('=' * 70)
