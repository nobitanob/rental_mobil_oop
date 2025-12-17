"""Cek Log Aktivitas"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_mobil_web.settings')
django.setup()

from rental.models import LogAktivitas

print('=' * 70)
print('  LOG AKTIVITAS - Semua Record')
print('=' * 70)

logs = LogAktivitas.objects.all().order_by('-created_at')[:15]
print(f'Total: {LogAktivitas.objects.count()} log\n')

for log in logs:
    icon = {'create': '+', 'update': '~', 'delete': 'X'}.get(log.aksi, '?')
    print(f'[{icon}] {log.aksi.upper()} | {log.model_name} #{log.object_id}')
    print(f'    {log.object_repr}')
    perubahan = log.perubahan[:80] + '...' if len(log.perubahan) > 80 else log.perubahan
    print(f'    {perubahan}')
    waktu = log.created_at.strftime("%Y-%m-%d %H:%M:%S")
    print(f'    {waktu}')
    print()
