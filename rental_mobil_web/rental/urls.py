"""
URL Configuration untuk API Rental Mobil
"""
from django.urls import path
from . import views

app_name = 'rental'

urlpatterns = [
    # ==========================================
    # NOTIFIKASI ENDPOINTS
    # ==========================================
    # GET - Daftar notifikasi
    path('api/notifikasi/', views.api_notifikasi_list, name='api_notifikasi_list'),
    
    # GET - Jumlah notifikasi belum dibaca
    path('api/notifikasi/unread-count/', views.api_notifikasi_unread_count, name='api_notifikasi_unread_count'),
    
    # POST - Buat notifikasi baru
    path('api/notifikasi/create/', views.api_notifikasi_create, name='api_notifikasi_create'),
    
    # POST - Tandai notifikasi sebagai dibaca
    path('api/notifikasi/<int:notifikasi_id>/mark-read/', views.api_notifikasi_mark_read, name='api_notifikasi_mark_read'),
    
    # POST - Tandai semua notifikasi sebagai dibaca
    path('api/notifikasi/mark-all-read/', views.api_notifikasi_mark_all_read, name='api_notifikasi_mark_all_read'),
    
    # ==========================================
    # ALERT ENDPOINTS
    # ==========================================
    # GET - Konfigurasi alert threshold
    path('api/alert/config/', views.api_alert_config, name='api_alert_config'),
    
    # GET - Cek keterlambatan
    path('api/alert/check-keterlambatan/', views.api_alert_check_keterlambatan, name='api_alert_check_keterlambatan'),
    
    # GET - Cek reminder jatuh tempo
    path('api/alert/check-reminder/', views.api_alert_check_reminder, name='api_alert_check_reminder'),
    
    # POST - Kirim notifikasi untuk semua alert
    path('api/alert/send-notifications/', views.api_alert_send_notifications, name='api_alert_send_notifications'),
    
    # ==========================================
    # MONITORING ENDPOINTS
    # ==========================================
    # GET - Dashboard statistik
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    
    # GET - Log aktivitas
    path('api/logs/', views.api_log_aktivitas, name='api_log_aktivitas'),
]
