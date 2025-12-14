"""
URL Configuration untuk Rental API
"""
from django.urls import path
from . import api_views

app_name = 'rental'

urlpatterns = [
    # Dashboard / Stats
    path('api/dashboard/', api_views.dashboard_stats, name='api_dashboard'),
    
    # Mobil endpoints
    path('api/mobil/', api_views.mobil_list, name='api_mobil_list'),
    path('api/mobil/<int:id>/', api_views.mobil_detail, name='api_mobil_detail'),
    
    # Pelanggan endpoints
    path('api/pelanggan/', api_views.pelanggan_list, name='api_pelanggan_list'),
    path('api/pelanggan/<int:id>/', api_views.pelanggan_detail, name='api_pelanggan_detail'),
    
    # Penyewaan endpoints
    path('api/penyewaan/', api_views.penyewaan_list, name='api_penyewaan_list'),
    path('api/penyewaan/<int:id>/', api_views.penyewaan_detail, name='api_penyewaan_detail'),
    path('api/penyewaan/<int:id>/kembalikan/', api_views.penyewaan_kembalikan, name='api_penyewaan_kembalikan'),
]
