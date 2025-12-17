"""Demo DELETE dengan Version Control"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_mobil_web.settings')
django.setup()

from rental.models import Mobil
from rental.version_control import VCS

print('=' * 70)
print('  DEMO DELETE + VERSION CONTROL')
print('=' * 70)

# Ambil mobil yang akan dihapus
mobil = Mobil.objects.get(id=19)
print('\n[1] DATA SEBELUM DELETE')
print('-' * 50)
print(f'   ID: {mobil.id}')
print(f'   Merk/Model: {mobil.merk} {mobil.model}')
print(f'   Plat: {mobil.plat_nomor}')
print(f'   Harga: Rp {mobil.harga_sewa_per_hari:,.0f}')
print(f'   Status: {mobil.status}')

# Commit sebelum delete (untuk backup)
VCS.commit_delete(mobil, 'Mobil Honda Civic dihapus dari sistem', user='admin')

# Delete
mobil_id = mobil.id
mobil.delete()

print('\n[2] DELETE EXECUTED')
print('-' * 50)
print(f'   Mobil ID {mobil_id} berhasil dihapus!')
print('   [COMMIT v4] Data dihapus (backup tersimpan)')

# Cek apakah masih ada
print('\n[3] VERIFIKASI DELETE')
print('-' * 50)
try:
    Mobil.objects.get(id=mobil_id)
    print('   ERROR: Mobil masih ada!')
except Mobil.DoesNotExist:
    print(f'   Mobil ID {mobil_id} sudah tidak ada di database')
    print('   DELETE berhasil!')

# Lihat history (data masih tersimpan di version control)
print('\n[4] VERSION HISTORY (Backup tersimpan)')
print('-' * 50)
history = VCS.get_history('Mobil', mobil_id)
for v in history:
    icons = {'create': '+', 'update': '~', 'delete': 'X', 'commit': '*', 'rollback': '<'}
    icon = icons.get(v.action, '?')
    print(f'   v{v.version} [{icon}] {v.action.upper()}: {v.commit_message}')
    print(f'       by {v.created_by} at {v.created_at.strftime("%H:%M:%S")}')

print('\n' + '=' * 70)
print('  Data terhapus tapi BACKUP tersimpan di Version Control!')
print('  Bisa di-ROLLBACK kapan saja.')
print('=' * 70)
