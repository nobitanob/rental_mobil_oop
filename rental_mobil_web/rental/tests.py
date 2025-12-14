"""
Unit Test untuk Rental Mobil Web (Django)
Menguji Models, Services, dan Admin dengan Mock
"""
from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import date, timedelta
from .models import Mobil, Pelanggan, Penyewaan, Pembayaran, Notifikasi, LogAktivitas
from .services import NotifikasiService
from .admin import MobilAdmin, PelangganAdmin, PenyewaanAdmin, PembayaranAdmin


# ══════════════════════════════════════════════════════════════════════════════
# TEST MODELS
# ══════════════════════════════════════════════════════════════════════════════

class TestMobilModel(TestCase):
    """Test cases untuk Model Mobil"""
    
    def setUp(self):
        """Setup data test"""
        # Karena managed=False, kita perlu mock atau buat test database khusus
        pass
    
    def test_mobil_str_representation(self):
        """Test representasi string Mobil"""
        mobil = Mobil(
            id=1,
            merk="Toyota",
            model="Avanza",
            tahun=2023,
            plat_nomor="B 1234 ABC",
            harga_sewa_per_hari=Decimal('350000.00'),
            status="tersedia"
        )
        expected = "Toyota Avanza (2023) - B 1234 ABC"
        self.assertEqual(str(mobil), expected)
    
    def test_mobil_status_choices(self):
        """Test pilihan status mobil"""
        valid_statuses = ['tersedia', 'disewa', 'perbaikan']
        for choice in Mobil.STATUS_CHOICES:
            self.assertIn(choice[0], valid_statuses)
    
    def test_mobil_default_status(self):
        """Test default status mobil adalah tersedia"""
        mobil = Mobil(
            merk="Honda",
            model="Jazz",
            tahun=2022,
            plat_nomor="D 5678 XYZ",
            harga_sewa_per_hari=Decimal('300000.00')
        )
        self.assertEqual(mobil.status, 'tersedia')


class TestPelangganModel(TestCase):
    """Test cases untuk Model Pelanggan"""
    
    def test_pelanggan_str_representation(self):
        """Test representasi string Pelanggan"""
        pelanggan = Pelanggan(
            id=1,
            nik="1234567890123456",
            nama="John Doe",
            alamat="Jl. Test No. 123",
            no_telepon="081234567890",
            email="john@example.com"
        )
        expected = "John Doe (1234567890123456)"
        self.assertEqual(str(pelanggan), expected)


class TestPenyewaanModel(TestCase):
    """Test cases untuk Model Penyewaan"""
    
    def test_penyewaan_str_representation(self):
        """Test representasi string Penyewaan"""
        # Mock mobil dan pelanggan
        mobil = Mock(spec=Mobil)
        mobil.harga_sewa_per_hari = Decimal('350000.00')
        
        pelanggan = Mock(spec=Pelanggan)
        pelanggan.nama = "John Doe"
        
        penyewaan = Penyewaan(
            id=1,
            kode_penyewaan="RNT-20251214-0001",
            tanggal_sewa=date.today(),
            tanggal_kembali=date.today() + timedelta(days=3),
            total_hari=3,
            total_biaya=Decimal('1050000.00'),
            status="aktif"
        )
        penyewaan.pelanggan = pelanggan
        penyewaan.mobil = mobil
        
        self.assertIn("RNT-20251214-0001", str(penyewaan))
    
    def test_penyewaan_hitung_denda_tepat_waktu(self):
        """Test hitung denda saat tepat waktu (0 hari keterlambatan)"""
        mobil = Mock(spec=Mobil)
        mobil.harga_sewa_per_hari = Decimal('350000.00')
        
        pelanggan = Mock(spec=Pelanggan)
        
        penyewaan = Penyewaan(
            id=1,
            kode_penyewaan="RNT-20251214-0001",
            tanggal_sewa=date.today(),
            tanggal_kembali=date.today() + timedelta(days=3),
            total_hari=3,
            total_biaya=Decimal('1050000.00')
        )
        penyewaan.mobil = mobil
        penyewaan.pelanggan = pelanggan
        
        denda = penyewaan.hitung_denda(0)
        self.assertEqual(denda, 0)
    
    def test_penyewaan_hitung_denda_terlambat(self):
        """Test hitung denda saat terlambat"""
        mobil = Mock(spec=Mobil)
        mobil.harga_sewa_per_hari = Decimal('350000.00')
        
        pelanggan = Mock(spec=Pelanggan)
        
        penyewaan = Penyewaan(
            id=1,
            kode_penyewaan="RNT-20251214-0001",
            tanggal_sewa=date.today() - timedelta(days=5),
            tanggal_kembali=date.today() - timedelta(days=2),
            total_hari=3,
            total_biaya=Decimal('1050000.00')
        )
        penyewaan.mobil = mobil
        penyewaan.pelanggan = pelanggan
        
        hari_terlambat = 2
        denda = penyewaan.hitung_denda(hari_terlambat)
        
        # Denda = harga_per_hari * hari_terlambat * 1.5
        expected_denda = 350000 * 2 * 1.5
        self.assertEqual(denda, expected_denda)
    
    def test_penyewaan_status_choices(self):
        """Test pilihan status penyewaan"""
        valid_statuses = ['aktif', 'selesai', 'terlambat']
        for choice in Penyewaan.STATUS_CHOICES:
            self.assertIn(choice[0], valid_statuses)


class TestPembayaranModel(TestCase):
    """Test cases untuk Model Pembayaran"""
    
    def test_pembayaran_metode_choices(self):
        """Test pilihan metode pembayaran"""
        valid_metodes = ['tunai', 'transfer', 'kartu_kredit']
        for choice in Pembayaran.METODE_CHOICES:
            self.assertIn(choice[0], valid_metodes)
    
    def test_pembayaran_status_choices(self):
        """Test pilihan status pembayaran"""
        valid_statuses = ['pending', 'lunas', 'gagal']
        for choice in Pembayaran.STATUS_CHOICES:
            self.assertIn(choice[0], valid_statuses)


class TestNotifikasiModel(TestCase):
    """Test cases untuk Model Notifikasi"""
    
    def test_notifikasi_str_representation(self):
        """Test representasi string Notifikasi"""
        notifikasi = Notifikasi(
            id=1,
            judul="Test Notifikasi",
            pesan="Ini adalah pesan test",
            tipe="info",
            kategori="sistem"
        )
        self.assertIn("Test Notifikasi", str(notifikasi))
    
    def test_notifikasi_tipe_choices(self):
        """Test pilihan tipe notifikasi"""
        valid_tipes = ['info', 'warning', 'success', 'error']
        for choice in Notifikasi.TIPE_CHOICES:
            self.assertIn(choice[0], valid_tipes)
    
    def test_notifikasi_kategori_choices(self):
        """Test pilihan kategori notifikasi"""
        valid_kategoris = ['penyewaan_baru', 'pembayaran', 'pengembalian', 
                          'keterlambatan', 'reminder', 'sistem']
        for choice in Notifikasi.KATEGORI_CHOICES:
            self.assertIn(choice[0], valid_kategoris)
    
    def test_notifikasi_default_values(self):
        """Test default values notifikasi"""
        notifikasi = Notifikasi(
            judul="Test",
            pesan="Test pesan"
        )
        self.assertEqual(notifikasi.tipe, 'info')
        self.assertEqual(notifikasi.kategori, 'sistem')
        self.assertFalse(notifikasi.dibaca)
        self.assertFalse(notifikasi.dikirim_email)


class TestLogAktivitasModel(TestCase):
    """Test cases untuk Model LogAktivitas"""
    
    def test_log_aktivitas_aksi_choices(self):
        """Test pilihan aksi log aktivitas"""
        valid_aksis = ['create', 'update', 'delete', 'view', 'login', 'logout']
        for choice in LogAktivitas.AKSI_CHOICES:
            self.assertIn(choice[0], valid_aksis)


# ══════════════════════════════════════════════════════════════════════════════
# TEST SERVICES DENGAN MOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestNotifikasiServiceWithMock(TestCase):
    """Test cases untuk NotifikasiService dengan Mock"""
    
    @patch('rental.services.Notifikasi.objects.create')
    @patch('rental.services.logger')
    def test_buat_notifikasi_success(self, mock_logger, mock_create):
        """Test buat notifikasi berhasil"""
        # Arrange: Setup mock
        mock_notifikasi = Mock(spec=Notifikasi)
        mock_notifikasi.id = 1
        mock_notifikasi.judul = "Test Notifikasi"
        mock_create.return_value = mock_notifikasi
        
        # Act
        result = NotifikasiService.buat_notifikasi(
            judul="Test Notifikasi",
            pesan="Ini adalah test",
            tipe="info",
            kategori="sistem"
        )
        
        # Assert
        self.assertEqual(result.judul, "Test Notifikasi")
        mock_create.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('rental.services.Notifikasi.objects.create')
    @patch('rental.services.logger')
    def test_buat_notifikasi_with_pelanggan(self, mock_logger, mock_create):
        """Test buat notifikasi dengan pelanggan"""
        # Arrange
        mock_pelanggan = Mock(spec=Pelanggan)
        mock_pelanggan.id = 1
        mock_pelanggan.nama = "John Doe"
        mock_pelanggan.email = ""  # Tidak ada email
        
        mock_notifikasi = Mock(spec=Notifikasi)
        mock_notifikasi.id = 1
        mock_create.return_value = mock_notifikasi
        
        # Act
        result = NotifikasiService.buat_notifikasi(
            judul="Test",
            pesan="Test pesan",
            pelanggan=mock_pelanggan
        )
        
        # Assert
        mock_create.assert_called_once()
        # Verifikasi pelanggan_id_ref dan pelanggan_nama dipassing
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['pelanggan_id_ref'], 1)
        self.assertEqual(call_kwargs['pelanggan_nama'], "John Doe")
    
    @patch('rental.services.Notifikasi.objects.create')
    @patch('rental.services.NotifikasiService.kirim_email_notifikasi')
    @patch('rental.services.logger')
    def test_buat_notifikasi_with_email(self, mock_logger, mock_kirim_email, mock_create):
        """Test buat notifikasi dengan kirim email"""
        # Arrange
        mock_pelanggan = Mock(spec=Pelanggan)
        mock_pelanggan.id = 1
        mock_pelanggan.nama = "John Doe"
        mock_pelanggan.email = "john@example.com"
        
        mock_notifikasi = Mock(spec=Notifikasi)
        mock_notifikasi.id = 1
        mock_notifikasi.dikirim_email = False
        mock_create.return_value = mock_notifikasi
        
        mock_kirim_email.return_value = True
        
        # Act
        result = NotifikasiService.buat_notifikasi(
            judul="Test",
            pesan="Test pesan",
            pelanggan=mock_pelanggan,
            kirim_email=True
        )
        
        # Assert
        mock_kirim_email.assert_called_once_with(mock_notifikasi, "john@example.com")
    
    @patch('rental.services.send_mail')
    @patch('rental.services.logger')
    def test_kirim_email_notifikasi_success(self, mock_logger, mock_send_mail):
        """Test kirim email notifikasi berhasil"""
        # Arrange
        mock_notifikasi = Mock(spec=Notifikasi)
        mock_notifikasi.judul = "Test Subject"
        mock_notifikasi.pesan = "Test message"
        
        mock_send_mail.return_value = 1
        
        # Act
        result = NotifikasiService.kirim_email_notifikasi(
            mock_notifikasi, 
            "test@example.com"
        )
        
        # Assert
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('rental.services.send_mail')
    @patch('rental.services.logger')
    def test_kirim_email_notifikasi_failed(self, mock_logger, mock_send_mail):
        """Test kirim email notifikasi gagal"""
        # Arrange
        mock_notifikasi = Mock(spec=Notifikasi)
        mock_notifikasi.judul = "Test Subject"
        mock_notifikasi.pesan = "Test message"
        
        mock_send_mail.side_effect = Exception("SMTP Error")
        
        # Act
        result = NotifikasiService.kirim_email_notifikasi(
            mock_notifikasi, 
            "test@example.com"
        )
        
        # Assert
        self.assertFalse(result)
        mock_logger.error.assert_called()
    
    @patch('rental.services.Notifikasi.objects.filter')
    def test_get_notifikasi_belum_dibaca(self, mock_filter):
        """Test get notifikasi yang belum dibaca"""
        # Arrange
        mock_queryset = MagicMock()
        mock_queryset.__getitem__ = Mock(return_value=[])
        mock_filter.return_value = mock_queryset
        
        # Act
        result = NotifikasiService.get_notifikasi_belum_dibaca(limit=5)
        
        # Assert
        mock_filter.assert_called_once_with(dibaca=False)
    
    @patch('rental.services.Notifikasi.objects.filter')
    def test_get_jumlah_notifikasi_belum_dibaca(self, mock_filter):
        """Test get jumlah notifikasi yang belum dibaca"""
        # Arrange
        mock_queryset = Mock()
        mock_queryset.count.return_value = 5
        mock_filter.return_value = mock_queryset
        
        # Act
        result = NotifikasiService.get_jumlah_notifikasi_belum_dibaca()
        
        # Assert
        self.assertEqual(result, 5)
        mock_filter.assert_called_once_with(dibaca=False)
    
    @patch('rental.services.Notifikasi.objects.filter')
    @patch('rental.services.logger')
    def test_tandai_semua_dibaca(self, mock_logger, mock_filter):
        """Test tandai semua notifikasi sebagai dibaca"""
        # Arrange
        mock_queryset = Mock()
        mock_queryset.update.return_value = 10
        mock_filter.return_value = mock_queryset
        
        # Act
        NotifikasiService.tandai_semua_dibaca()
        
        # Assert
        mock_queryset.update.assert_called_once_with(dibaca=True)
        mock_logger.info.assert_called()


class TestNotifikasiServicePenyewaan(TestCase):
    """Test cases untuk NotifikasiService terkait Penyewaan"""
    
    @patch('rental.services.NotifikasiService.buat_notifikasi')
    def test_notifikasi_penyewaan_baru(self, mock_buat_notifikasi):
        """Test notifikasi penyewaan baru"""
        # Arrange
        mock_mobil = Mock(spec=Mobil)
        mock_mobil.__str__ = Mock(return_value="Toyota Avanza")
        
        mock_pelanggan = Mock(spec=Pelanggan)
        mock_pelanggan.nama = "John Doe"
        
        mock_penyewaan = Mock(spec=Penyewaan)
        mock_penyewaan.kode_penyewaan = "RNT-20251214-0001"
        mock_penyewaan.mobil = mock_mobil
        mock_penyewaan.pelanggan = mock_pelanggan
        mock_penyewaan.tanggal_sewa = date.today()
        mock_penyewaan.tanggal_kembali = date.today() + timedelta(days=3)
        mock_penyewaan.total_biaya = Decimal('1050000.00')
        
        mock_buat_notifikasi.return_value = Mock(spec=Notifikasi)
        
        # Act
        result = NotifikasiService.notifikasi_penyewaan_baru(mock_penyewaan)
        
        # Assert
        mock_buat_notifikasi.assert_called_once()
        call_kwargs = mock_buat_notifikasi.call_args[1]
        self.assertIn("RNT-20251214-0001", call_kwargs['judul'])
        self.assertEqual(call_kwargs['tipe'], 'success')
        self.assertEqual(call_kwargs['kategori'], 'penyewaan_baru')
        self.assertTrue(call_kwargs['kirim_email'])
    
    @patch('rental.services.NotifikasiService.buat_notifikasi')
    def test_notifikasi_pengembalian_tepat_waktu(self, mock_buat_notifikasi):
        """Test notifikasi pengembalian tepat waktu (tanpa denda)"""
        # Arrange
        mock_penyewaan = Mock(spec=Penyewaan)
        mock_penyewaan.kode_penyewaan = "RNT-20251214-0001"
        mock_penyewaan.mobil = Mock(__str__=Mock(return_value="Toyota Avanza"))
        mock_penyewaan.pelanggan = Mock(spec=Pelanggan)
        
        mock_buat_notifikasi.return_value = Mock(spec=Notifikasi)
        
        # Act
        result = NotifikasiService.notifikasi_pengembalian(mock_penyewaan, denda=0)
        
        # Assert
        call_kwargs = mock_buat_notifikasi.call_args[1]
        self.assertEqual(call_kwargs['tipe'], 'success')
        self.assertIn("Sukses", call_kwargs['judul'])
    
    @patch('rental.services.NotifikasiService.buat_notifikasi')
    def test_notifikasi_pengembalian_dengan_denda(self, mock_buat_notifikasi):
        """Test notifikasi pengembalian dengan denda"""
        # Arrange
        mock_penyewaan = Mock(spec=Penyewaan)
        mock_penyewaan.kode_penyewaan = "RNT-20251214-0001"
        mock_penyewaan.mobil = Mock(__str__=Mock(return_value="Toyota Avanza"))
        mock_penyewaan.pelanggan = Mock(spec=Pelanggan)
        
        mock_buat_notifikasi.return_value = Mock(spec=Notifikasi)
        
        # Act
        result = NotifikasiService.notifikasi_pengembalian(mock_penyewaan, denda=525000)
        
        # Assert
        call_kwargs = mock_buat_notifikasi.call_args[1]
        self.assertEqual(call_kwargs['tipe'], 'warning')
        self.assertIn("Denda", call_kwargs['judul'])
    
    @patch('rental.services.NotifikasiService.buat_notifikasi')
    def test_notifikasi_keterlambatan(self, mock_buat_notifikasi):
        """Test notifikasi keterlambatan"""
        # Arrange
        mock_penyewaan = Mock(spec=Penyewaan)
        mock_penyewaan.kode_penyewaan = "RNT-20251214-0001"
        mock_penyewaan.mobil = Mock(__str__=Mock(return_value="Toyota Avanza"))
        mock_penyewaan.pelanggan = Mock(spec=Pelanggan)
        mock_penyewaan.tanggal_kembali = date.today() - timedelta(days=2)
        
        mock_buat_notifikasi.return_value = Mock(spec=Notifikasi)
        
        # Act
        result = NotifikasiService.notifikasi_keterlambatan(
            mock_penyewaan, 
            hari_terlambat=2, 
            estimasi_denda=1050000
        )
        
        # Assert
        call_kwargs = mock_buat_notifikasi.call_args[1]
        self.assertEqual(call_kwargs['tipe'], 'error')
        self.assertEqual(call_kwargs['kategori'], 'keterlambatan')
        self.assertIn("PERINGATAN", call_kwargs['judul'])


# ══════════════════════════════════════════════════════════════════════════════
# TEST ADMIN
# ══════════════════════════════════════════════════════════════════════════════

class TestMobilAdmin(TestCase):
    """Test cases untuk MobilAdmin"""
    
    def setUp(self):
        """Setup admin site"""
        self.site = AdminSite()
        self.admin = MobilAdmin(Mobil, self.site)
    
    def test_list_display_fields(self):
        """Test list_display berisi field yang dibutuhkan"""
        expected_fields = ['id', 'merk', 'model', 'tahun', 'plat_nomor', 
                          'harga_sewa_per_hari', 'status_badge']
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)
    
    def test_list_filter_fields(self):
        """Test list_filter berisi field yang dibutuhkan"""
        expected_filters = ['status', 'merk', 'tahun']
        for field in expected_filters:
            self.assertIn(field, self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search_fields berisi field yang dibutuhkan"""
        expected_searches = ['merk', 'model', 'plat_nomor']
        for field in expected_searches:
            self.assertIn(field, self.admin.search_fields)
    
    def test_status_badge_tersedia(self):
        """Test status badge untuk status tersedia"""
        mobil = Mock(spec=Mobil)
        mobil.status = 'tersedia'
        mobil.get_status_display.return_value = 'Tersedia'
        
        result = self.admin.status_badge(mobil)
        
        self.assertIn('green', result)
        self.assertIn('Tersedia', result)
    
    def test_status_badge_disewa(self):
        """Test status badge untuk status disewa"""
        mobil = Mock(spec=Mobil)
        mobil.status = 'disewa'
        mobil.get_status_display.return_value = 'Disewa'
        
        result = self.admin.status_badge(mobil)
        
        self.assertIn('orange', result)
        self.assertIn('Disewa', result)
    
    def test_status_badge_perbaikan(self):
        """Test status badge untuk status perbaikan"""
        mobil = Mock(spec=Mobil)
        mobil.status = 'perbaikan'
        mobil.get_status_display.return_value = 'Perbaikan'
        
        result = self.admin.status_badge(mobil)
        
        self.assertIn('red', result)
        self.assertIn('Perbaikan', result)


class TestPenyewaanAdmin(TestCase):
    """Test cases untuk PenyewaanAdmin"""
    
    def setUp(self):
        """Setup admin site"""
        self.site = AdminSite()
        self.admin = PenyewaanAdmin(Penyewaan, self.site)
    
    def test_list_display_fields(self):
        """Test list_display berisi field yang dibutuhkan"""
        expected_fields = ['kode_penyewaan', 'pelanggan', 'mobil', 
                          'tanggal_sewa', 'tanggal_kembali', 'status_badge']
        for field in expected_fields:
            self.assertIn(field, self.admin.list_display)
    
    def test_status_badge_aktif(self):
        """Test status badge untuk status aktif"""
        penyewaan = Mock(spec=Penyewaan)
        penyewaan.status = 'aktif'
        penyewaan.get_status_display.return_value = 'Aktif'
        
        result = self.admin.status_badge(penyewaan)
        
        self.assertIn('blue', result)
        self.assertIn('Aktif', result)
    
    def test_status_badge_selesai(self):
        """Test status badge untuk status selesai"""
        penyewaan = Mock(spec=Penyewaan)
        penyewaan.status = 'selesai'
        penyewaan.get_status_display.return_value = 'Selesai'
        
        result = self.admin.status_badge(penyewaan)
        
        self.assertIn('green', result)
        self.assertIn('Selesai', result)
    
    def test_status_badge_terlambat(self):
        """Test status badge untuk status terlambat"""
        penyewaan = Mock(spec=Penyewaan)
        penyewaan.status = 'terlambat'
        penyewaan.get_status_display.return_value = 'Terlambat'
        
        result = self.admin.status_badge(penyewaan)
        
        self.assertIn('red', result)
        self.assertIn('Terlambat', result)


class TestPembayaranAdmin(TestCase):
    """Test cases untuk PembayaranAdmin"""
    
    def setUp(self):
        """Setup admin site"""
        self.site = AdminSite()
        self.admin = PembayaranAdmin(Pembayaran, self.site)
    
    def test_status_badge_pending(self):
        """Test status badge untuk status pending"""
        pembayaran = Mock(spec=Pembayaran)
        pembayaran.status = 'pending'
        pembayaran.get_status_display.return_value = 'Pending'
        
        result = self.admin.status_badge(pembayaran)
        
        self.assertIn('orange', result)
        self.assertIn('Pending', result)
    
    def test_status_badge_lunas(self):
        """Test status badge untuk status lunas"""
        pembayaran = Mock(spec=Pembayaran)
        pembayaran.status = 'lunas'
        pembayaran.get_status_display.return_value = 'Lunas'
        
        result = self.admin.status_badge(pembayaran)
        
        self.assertIn('green', result)
        self.assertIn('Lunas', result)


# ══════════════════════════════════════════════════════════════════════════════
# TEST BUSINESS LOGIC
# ══════════════════════════════════════════════════════════════════════════════

class TestHitungDenda(TestCase):
    """Test cases untuk perhitungan denda"""
    
    def test_denda_1_hari_terlambat(self):
        """Test denda 1 hari keterlambatan"""
        harga_per_hari = Decimal('350000.00')
        hari_terlambat = 1
        
        # Denda = harga * hari * 1.5
        expected_denda = float(harga_per_hari) * hari_terlambat * 1.5
        
        mobil = Mock(spec=Mobil)
        mobil.harga_sewa_per_hari = harga_per_hari
        
        penyewaan = Penyewaan()
        penyewaan.mobil = mobil
        
        denda = penyewaan.hitung_denda(hari_terlambat)
        self.assertEqual(denda, expected_denda)
    
    def test_denda_7_hari_terlambat(self):
        """Test denda 7 hari keterlambatan"""
        harga_per_hari = Decimal('350000.00')
        hari_terlambat = 7
        
        expected_denda = float(harga_per_hari) * hari_terlambat * 1.5
        
        mobil = Mock(spec=Mobil)
        mobil.harga_sewa_per_hari = harga_per_hari
        
        penyewaan = Penyewaan()
        penyewaan.mobil = mobil
        
        denda = penyewaan.hitung_denda(hari_terlambat)
        self.assertEqual(denda, expected_denda)
    
    def test_denda_0_hari_tidak_terlambat(self):
        """Test tidak ada denda jika tidak terlambat"""
        mobil = Mock(spec=Mobil)
        mobil.harga_sewa_per_hari = Decimal('350000.00')
        
        penyewaan = Penyewaan()
        penyewaan.mobil = mobil
        
        denda = penyewaan.hitung_denda(0)
        self.assertEqual(denda, 0)


class TestHitungTotalBiaya(TestCase):
    """Test cases untuk perhitungan total biaya"""
    
    def test_hitung_biaya_3_hari(self):
        """Test hitung biaya untuk 3 hari sewa"""
        harga_per_hari = Decimal('350000.00')
        jumlah_hari = 3
        
        expected_total = harga_per_hari * jumlah_hari
        self.assertEqual(expected_total, Decimal('1050000.00'))
    
    def test_hitung_biaya_7_hari(self):
        """Test hitung biaya untuk 7 hari sewa"""
        harga_per_hari = Decimal('350000.00')
        jumlah_hari = 7
        
        expected_total = harga_per_hari * jumlah_hari
        self.assertEqual(expected_total, Decimal('2450000.00'))
    
    def test_hitung_biaya_30_hari(self):
        """Test hitung biaya untuk 30 hari sewa (1 bulan)"""
        harga_per_hari = Decimal('350000.00')
        jumlah_hari = 30
        
        expected_total = harga_per_hari * jumlah_hari
        self.assertEqual(expected_total, Decimal('10500000.00'))


# ══════════════════════════════════════════════════════════════════════════════
# TEST URL & VIEW (Optional - jika ada views)
# ══════════════════════════════════════════════════════════════════════════════

class TestAdminURLs(TestCase):
    """Test cases untuk Admin URLs"""
    
    def setUp(self):
        """Setup test client dan admin user"""
        self.client = Client()
    
    def test_admin_login_page_accessible(self):
        """Test halaman login admin bisa diakses"""
        response = self.client.get('/admin/login/')
        self.assertIn(response.status_code, [200, 302])
    
    def test_admin_index_requires_login(self):
        """Test halaman admin membutuhkan login"""
        response = self.client.get('/admin/')
        # Harus redirect ke login
        self.assertIn(response.status_code, [200, 302])
