"""Script untuk membuat notifikasi demo"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_mobil_web.settings')
django.setup()

from rental.models import Notifikasi

# Buat notifikasi demo
notifikasi_data = [
    {'judul': 'Selamat Datang di Sistem Rental', 'pesan': 'Sistem rental mobil sudah siap digunakan.', 'tipe': 'success', 'kategori': 'sistem'},
    {'judul': 'Mobil Baru Ditambahkan', 'pesan': 'Toyota Avanza berhasil ditambahkan ke database.', 'tipe': 'info', 'kategori': 'mobil'},
    {'judul': 'Pelanggan Baru Terdaftar', 'pesan': 'Pelanggan baru telah mendaftar di sistem.', 'tipe': 'info', 'kategori': 'pelanggan'},
    {'judul': 'Penyewaan Aktif', 'pesan': 'Ada penyewaan baru yang sedang berjalan.', 'tipe': 'warning', 'kategori': 'penyewaan'},
    {'judul': 'Pembayaran Berhasil', 'pesan': 'Pembayaran telah dikonfirmasi.', 'tipe': 'success', 'kategori': 'pembayaran'},
]

for data in notifikasi_data:
    Notifikasi.objects.create(**data)
    print(f"Created: {data['judul']}")

print(f"\nTotal Notifikasi: {Notifikasi.objects.count()}")
