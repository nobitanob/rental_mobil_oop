"""
Views untuk API Notifikasi dan Alert System
"""
import json
import logging
from datetime import date, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Notifikasi, Penyewaan, Pelanggan, Mobil, LogAktivitas
from .services import NotifikasiService

logger = logging.getLogger('rental.notifikasi')


# ==========================================
# KONFIGURASI ALERT THRESHOLD
# ==========================================
ALERT_CONFIG = {
    # Threshold untuk reminder (hari sebelum jatuh tempo)
    'reminder_days': [1, 3, 7],
    
    # Threshold untuk level keterlambatan
    'keterlambatan': {
        'warning': 1,      # 1-3 hari = warning (kuning)
        'danger': 3,       # 3-7 hari = danger (orange) 
        'critical': 7,     # >7 hari = critical (merah)
    },
    
    # Threshold untuk denda
    'denda': {
        'low': 100000,       # < 100rb = rendah
        'medium': 500000,    # 100rb - 500rb = sedang
        'high': 1000000,     # > 1jt = tinggi
    },
    
    # Notifikasi yang diaktifkan
    'enabled_notifications': {
        'penyewaan_baru': True,
        'pembayaran': True,
        'reminder': True,
        'keterlambatan': True,
        'pengembalian': True,
    }
}


# ==========================================
# API ENDPOINTS
# ==========================================

@csrf_exempt
@require_http_methods(["GET"])
def api_notifikasi_list(request):
    """
    GET /api/notifikasi/
    Mengambil daftar semua notifikasi
    
    Query params:
    - limit: jumlah data (default 20)
    - status: 'dibaca' atau 'belum_dibaca'
    - tipe: info, warning, success, error
    - kategori: penyewaan_baru, pembayaran, dll
    """
    try:
        limit = int(request.GET.get('limit', 20))
        status = request.GET.get('status', None)
        tipe = request.GET.get('tipe', None)
        kategori = request.GET.get('kategori', None)
        
        queryset = Notifikasi.objects.all()
        
        if status == 'dibaca':
            queryset = queryset.filter(dibaca=True)
        elif status == 'belum_dibaca':
            queryset = queryset.filter(dibaca=False)
        
        if tipe:
            queryset = queryset.filter(tipe=tipe)
        
        if kategori:
            queryset = queryset.filter(kategori=kategori)
        
        queryset = queryset.order_by('-created_at')[:limit]
        
        data = [{
            'id': n.id,
            'judul': n.judul,
            'pesan': n.pesan,
            'tipe': n.tipe,
            'kategori': n.kategori,
            'pelanggan_nama': n.pelanggan_nama,
            'dibaca': n.dibaca,
            'dikirim_email': n.dikirim_email,
            'created_at': n.created_at.isoformat() if n.created_at else None,
        } for n in queryset]
        
        logger.info(f"API: Mengambil {len(data)} notifikasi")
        
        return JsonResponse({
            'success': True,
            'count': len(data),
            'data': data
        })
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_notifikasi_unread_count(request):
    """
    GET /api/notifikasi/unread-count/
    Mengambil jumlah notifikasi yang belum dibaca
    """
    try:
        count = NotifikasiService.get_jumlah_notifikasi_belum_dibaca()
        
        return JsonResponse({
            'success': True,
            'unread_count': count
        })
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_notifikasi_mark_read(request, notifikasi_id):
    """
    POST /api/notifikasi/<id>/mark-read/
    Menandai notifikasi sebagai sudah dibaca
    """
    try:
        notifikasi = Notifikasi.objects.get(id=notifikasi_id)
        notifikasi.tandai_dibaca()
        
        logger.info(f"API: Notifikasi {notifikasi_id} ditandai dibaca")
        
        return JsonResponse({
            'success': True,
            'message': f'Notifikasi {notifikasi_id} ditandai sebagai dibaca'
        })
        
    except Notifikasi.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notifikasi tidak ditemukan'
        }, status=404)
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_notifikasi_mark_all_read(request):
    """
    POST /api/notifikasi/mark-all-read/
    Menandai semua notifikasi sebagai sudah dibaca
    """
    try:
        NotifikasiService.tandai_semua_dibaca()
        
        logger.info("API: Semua notifikasi ditandai dibaca")
        
        return JsonResponse({
            'success': True,
            'message': 'Semua notifikasi ditandai sebagai dibaca'
        })
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_notifikasi_create(request):
    """
    POST /api/notifikasi/create/
    Membuat notifikasi baru (manual)
    
    Body JSON:
    {
        "judul": "Judul notifikasi",
        "pesan": "Isi pesan",
        "tipe": "info|warning|success|error",
        "kategori": "sistem"
    }
    """
    try:
        data = json.loads(request.body)
        
        judul = data.get('judul', 'Notifikasi')
        pesan = data.get('pesan', '')
        tipe = data.get('tipe', 'info')
        kategori = data.get('kategori', 'sistem')
        
        notifikasi = NotifikasiService.buat_notifikasi(
            judul=judul,
            pesan=pesan,
            tipe=tipe,
            kategori=kategori
        )
        
        logger.info(f"API: Notifikasi baru dibuat - {judul}")
        
        return JsonResponse({
            'success': True,
            'message': 'Notifikasi berhasil dibuat',
            'data': {
                'id': notifikasi.id,
                'judul': notifikasi.judul,
                'tipe': notifikasi.tipe,
            }
        }, status=201)
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_alert_config(request):
    """
    GET /api/alert/config/
    Mengambil konfigurasi alert threshold
    """
    return JsonResponse({
        'success': True,
        'config': ALERT_CONFIG
    })


@csrf_exempt
@require_http_methods(["GET"])
def api_alert_check_keterlambatan(request):
    """
    GET /api/alert/check-keterlambatan/
    Mengecek semua penyewaan yang terlambat dan mengembalikan alert
    """
    try:
        today = date.today()
        
        # Ambil penyewaan aktif yang sudah melewati tanggal kembali
        penyewaan_terlambat = Penyewaan.objects.filter(
            status__in=['aktif', 'terlambat'],
            tanggal_kembali__lt=today
        )
        
        alerts = []
        for p in penyewaan_terlambat:
            hari_terlambat = (today - p.tanggal_kembali).days
            estimasi_denda = p.hitung_denda(hari_terlambat)
            
            # Tentukan level alert berdasarkan threshold
            if hari_terlambat >= ALERT_CONFIG['keterlambatan']['critical']:
                level = 'critical'
                tipe = 'error'
            elif hari_terlambat >= ALERT_CONFIG['keterlambatan']['danger']:
                level = 'danger'
                tipe = 'error'
            else:
                level = 'warning'
                tipe = 'warning'
            
            alerts.append({
                'kode_penyewaan': p.kode_penyewaan,
                'pelanggan': p.pelanggan.nama if p.pelanggan else 'Unknown',
                'mobil': str(p.mobil) if p.mobil else 'Unknown',
                'tanggal_kembali': p.tanggal_kembali.isoformat(),
                'hari_terlambat': hari_terlambat,
                'estimasi_denda': float(estimasi_denda),
                'level': level,
                'tipe': tipe,
            })
        
        # Sort by hari_terlambat descending
        alerts.sort(key=lambda x: x['hari_terlambat'], reverse=True)
        
        logger.info(f"API: Cek keterlambatan - {len(alerts)} alert ditemukan")
        
        return JsonResponse({
            'success': True,
            'total_alerts': len(alerts),
            'threshold': ALERT_CONFIG['keterlambatan'],
            'alerts': alerts
        })
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_alert_check_reminder(request):
    """
    GET /api/alert/check-reminder/
    Mengecek penyewaan yang akan jatuh tempo dan mengembalikan reminder
    """
    try:
        today = date.today()
        reminders = []
        
        for days in ALERT_CONFIG['reminder_days']:
            target_date = today + timedelta(days=days)
            
            penyewaan_list = Penyewaan.objects.filter(
                status='aktif',
                tanggal_kembali=target_date
            )
            
            for p in penyewaan_list:
                reminders.append({
                    'kode_penyewaan': p.kode_penyewaan,
                    'pelanggan': p.pelanggan.nama if p.pelanggan else 'Unknown',
                    'mobil': str(p.mobil) if p.mobil else 'Unknown',
                    'tanggal_kembali': p.tanggal_kembali.isoformat(),
                    'hari_tersisa': days,
                    'tipe': 'info' if days > 1 else 'warning',
                })
        
        # Sort by hari_tersisa ascending
        reminders.sort(key=lambda x: x['hari_tersisa'])
        
        logger.info(f"API: Cek reminder - {len(reminders)} reminder ditemukan")
        
        return JsonResponse({
            'success': True,
            'total_reminders': len(reminders),
            'reminder_days': ALERT_CONFIG['reminder_days'],
            'reminders': reminders
        })
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_alert_send_notifications(request):
    """
    POST /api/alert/send-notifications/
    Mengirim notifikasi untuk semua alert yang ditemukan
    
    Body JSON (optional):
    {
        "include_reminder": true,
        "include_keterlambatan": true
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        include_reminder = data.get('include_reminder', True)
        include_keterlambatan = data.get('include_keterlambatan', True)
        
        today = date.today()
        notifications_sent = {
            'reminder': 0,
            'keterlambatan': 0
        }
        
        # Kirim reminder
        if include_reminder and ALERT_CONFIG['enabled_notifications']['reminder']:
            for days in ALERT_CONFIG['reminder_days']:
                target_date = today + timedelta(days=days)
                penyewaan_list = Penyewaan.objects.filter(
                    status='aktif',
                    tanggal_kembali=target_date
                )
                
                for p in penyewaan_list:
                    NotifikasiService.notifikasi_reminder_pengembalian(p, days)
                    notifications_sent['reminder'] += 1
        
        # Kirim notifikasi keterlambatan
        if include_keterlambatan and ALERT_CONFIG['enabled_notifications']['keterlambatan']:
            penyewaan_terlambat = Penyewaan.objects.filter(
                status__in=['aktif', 'terlambat'],
                tanggal_kembali__lt=today
            )
            
            for p in penyewaan_terlambat:
                hari_terlambat = (today - p.tanggal_kembali).days
                estimasi_denda = p.hitung_denda(hari_terlambat)
                
                # Update status
                if p.status != 'terlambat':
                    p.status = 'terlambat'
                    p.save()
                
                NotifikasiService.notifikasi_keterlambatan(p, hari_terlambat, estimasi_denda)
                notifications_sent['keterlambatan'] += 1
        
        total = notifications_sent['reminder'] + notifications_sent['keterlambatan']
        logger.info(f"API: {total} notifikasi dikirim")
        
        return JsonResponse({
            'success': True,
            'message': f'{total} notifikasi berhasil dikirim',
            'details': notifications_sent
        })
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_dashboard_stats(request):
    """
    GET /api/dashboard/stats/
    Mengambil statistik untuk dashboard monitoring
    """
    try:
        today = date.today()
        
        # Statistik penyewaan
        total_penyewaan = Penyewaan.objects.count()
        penyewaan_aktif = Penyewaan.objects.filter(status='aktif').count()
        penyewaan_terlambat = Penyewaan.objects.filter(status='terlambat').count()
        penyewaan_selesai = Penyewaan.objects.filter(status='selesai').count()
        
        # Statistik mobil
        total_mobil = Mobil.objects.count()
        mobil_tersedia = Mobil.objects.filter(status='tersedia').count()
        mobil_disewa = Mobil.objects.filter(status='disewa').count()
        
        # Statistik notifikasi
        notifikasi_belum_dibaca = NotifikasiService.get_jumlah_notifikasi_belum_dibaca()
        
        # Alert counts
        penyewaan_akan_jatuh_tempo = Penyewaan.objects.filter(
            status='aktif',
            tanggal_kembali__lte=today + timedelta(days=3),
            tanggal_kembali__gte=today
        ).count()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'penyewaan': {
                    'total': total_penyewaan,
                    'aktif': penyewaan_aktif,
                    'terlambat': penyewaan_terlambat,
                    'selesai': penyewaan_selesai,
                },
                'mobil': {
                    'total': total_mobil,
                    'tersedia': mobil_tersedia,
                    'disewa': mobil_disewa,
                },
                'alerts': {
                    'notifikasi_belum_dibaca': notifikasi_belum_dibaca,
                    'penyewaan_terlambat': penyewaan_terlambat,
                    'akan_jatuh_tempo': penyewaan_akan_jatuh_tempo,
                }
            }
        })
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_log_aktivitas(request):
    """
    GET /api/logs/
    Mengambil log aktivitas terbaru
    
    Query params:
    - limit: jumlah data (default 50)
    - aksi: filter berdasarkan aksi (create, update, delete, login, logout)
    - model: filter berdasarkan model_name
    """
    try:
        limit = int(request.GET.get('limit', 50))
        aksi = request.GET.get('aksi', None)
        model = request.GET.get('model', None)
        
        queryset = LogAktivitas.objects.all()
        
        if aksi:
            queryset = queryset.filter(aksi=aksi)
        
        if model:
            queryset = queryset.filter(model_name__icontains=model)
        
        queryset = queryset.order_by('-created_at')[:limit]
        
        data = [{
            'id': log.id,
            'user': log.user,
            'aksi': log.aksi,
            'model_name': log.model_name,
            'object_repr': log.object_repr,
            'perubahan': log.perubahan,
            'ip_address': log.ip_address,
            'created_at': log.created_at.isoformat() if log.created_at else None,
        } for log in queryset]
        
        return JsonResponse({
            'success': True,
            'count': len(data),
            'data': data
        })
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
