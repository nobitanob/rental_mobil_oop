"""Tampilkan Log Aktivitas dengan format tabel"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_mobil_web.settings')
django.setup()

from rental.models import LogAktivitas

print('=' * 90)
print('  LOG AKTIVITAS - 15 Record Terbaru')
print('=' * 90)
print()

header = f"{'ID':<5} {'User':<12} {'Aksi':<8} {'Model':<12} {'Object':<28} {'Waktu':<18}"
print(header)
print('-' * 90)

logs = LogAktivitas.objects.all().order_by('-created_at')[:15]
for log in logs:
    obj = log.object_repr[:26] + '..' if len(log.object_repr) > 28 else log.object_repr
    waktu = log.created_at.strftime('%Y-%m-%d %H:%M')
    row = f"{log.id:<5} {log.user:<12} {log.aksi:<8} {log.model_name:<12} {obj:<28} {waktu:<18}"
    print(row)

print()
print('=' * 90)
print('NOTE:')
print('  - User = "system" jika operasi dari CLI/script (tanpa HTTP request)')
print('  - User = username jika dari Django Admin dengan user yang login')
print('  - Cek di /admin/rental/logaktivitas/ untuk melihat via web')
print('=' * 90)
