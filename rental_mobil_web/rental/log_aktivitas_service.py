"""
============================================
LOG AKTIVITAS SERVICE
============================================
Service untuk mengelola log aktivitas dengan fitur:
- Tracking perubahan field (before/after)
- CRUD operations untuk LogAktivitas
- Export log ke file
- Statistik aktivitas
============================================
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.db import models
from django.contrib.auth import get_user_model

logger = logging.getLogger('rental.log_aktivitas')


class LogAktivitasService:
    """Service untuk mengelola Log Aktivitas"""
    
    # Cache untuk menyimpan data sebelum update
    _pre_save_cache: Dict[str, Dict] = {}
    
    @classmethod
    def get_model(cls):
        """Lazy import LogAktivitas model"""
        from .models import LogAktivitas
        return LogAktivitas
    
    # ==========================================
    # CREATE
    # ==========================================
    
    @classmethod
    def create_log(
        cls,
        aksi: str,
        model_name: str,
        object_id: int = None,
        object_repr: str = '',
        perubahan: str = '',
        user: str = 'system',
        ip_address: str = None,
        user_agent: str = ''
    ) -> 'LogAktivitas':
        """
        Membuat log aktivitas baru
        
        Args:
            aksi: 'create', 'update', 'delete', 'view', 'login', 'logout'
            model_name: Nama model (Mobil, Pelanggan, dll)
            object_id: ID objek yang diubah
            object_repr: String representasi objek
            perubahan: Detail perubahan
            user: Username yang melakukan aksi
            ip_address: IP address user
            user_agent: Browser user agent
        
        Returns:
            LogAktivitas instance
        """
        LogAktivitas = cls.get_model()
        
        log = LogAktivitas.objects.create(
            aksi=aksi,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            perubahan=perubahan,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"Log created: [{aksi}] {model_name} - {object_repr}")
        return log
    
    # ==========================================
    # READ
    # ==========================================
    
    @classmethod
    def get_by_id(cls, log_id: int) -> Optional['LogAktivitas']:
        """Ambil log berdasarkan ID"""
        LogAktivitas = cls.get_model()
        try:
            return LogAktivitas.objects.get(id=log_id)
        except LogAktivitas.DoesNotExist:
            return None
    
    @classmethod
    def get_all(cls, limit: int = 100) -> List['LogAktivitas']:
        """Ambil semua log dengan limit"""
        LogAktivitas = cls.get_model()
        return list(LogAktivitas.objects.all()[:limit])
    
    @classmethod
    def get_by_model(cls, model_name: str, limit: int = 50) -> List['LogAktivitas']:
        """Ambil log berdasarkan model"""
        LogAktivitas = cls.get_model()
        return list(LogAktivitas.objects.filter(model_name=model_name)[:limit])
    
    @classmethod
    def get_by_aksi(cls, aksi: str, limit: int = 50) -> List['LogAktivitas']:
        """Ambil log berdasarkan aksi"""
        LogAktivitas = cls.get_model()
        return list(LogAktivitas.objects.filter(aksi=aksi)[:limit])
    
    @classmethod
    def get_by_user(cls, user: str, limit: int = 50) -> List['LogAktivitas']:
        """Ambil log berdasarkan user"""
        LogAktivitas = cls.get_model()
        return list(LogAktivitas.objects.filter(user=user)[:limit])
    
    @classmethod
    def get_by_object(cls, model_name: str, object_id: int) -> List['LogAktivitas']:
        """Ambil riwayat log untuk objek tertentu"""
        LogAktivitas = cls.get_model()
        return list(LogAktivitas.objects.filter(
            model_name=model_name,
            object_id=object_id
        ))
    
    @classmethod
    def get_by_date_range(
        cls, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 100
    ) -> List['LogAktivitas']:
        """Ambil log berdasarkan range tanggal"""
        LogAktivitas = cls.get_model()
        return list(LogAktivitas.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )[:limit])
    
    @classmethod
    def get_recent(cls, hours: int = 24) -> List['LogAktivitas']:
        """Ambil log dalam X jam terakhir"""
        LogAktivitas = cls.get_model()
        since = datetime.now() - timedelta(hours=hours)
        return list(LogAktivitas.objects.filter(created_at__gte=since))
    
    # ==========================================
    # UPDATE (untuk keperluan admin)
    # ==========================================
    
    @classmethod
    def update_log(
        cls, 
        log_id: int, 
        perubahan: str = None,
        object_repr: str = None
    ) -> Optional['LogAktivitas']:
        """
        Update log aktivitas (hanya field tertentu yang boleh diubah)
        Biasanya untuk menambah catatan atau koreksi
        
        Args:
            log_id: ID log yang akan diupdate
            perubahan: Detail perubahan baru
            object_repr: Representasi objek baru
        
        Returns:
            LogAktivitas yang sudah diupdate atau None
        """
        log = cls.get_by_id(log_id)
        if not log:
            logger.warning(f"Log ID {log_id} not found for update")
            return None
        
        updated_fields = []
        
        if perubahan is not None:
            old_perubahan = log.perubahan
            log.perubahan = perubahan
            updated_fields.append(f"perubahan: '{old_perubahan}' → '{perubahan}'")
        
        if object_repr is not None:
            old_repr = log.object_repr
            log.object_repr = object_repr
            updated_fields.append(f"object_repr: '{old_repr}' → '{object_repr}'")
        
        if updated_fields:
            log.save()
            logger.info(f"Log ID {log_id} updated: {', '.join(updated_fields)}")
        
        return log
    
    @classmethod
    def add_note_to_log(cls, log_id: int, note: str) -> Optional['LogAktivitas']:
        """Tambahkan catatan ke log yang sudah ada"""
        log = cls.get_by_id(log_id)
        if not log:
            return None
        
        if log.perubahan:
            log.perubahan = f"{log.perubahan}\n[NOTE] {note}"
        else:
            log.perubahan = f"[NOTE] {note}"
        
        log.save()
        logger.info(f"Note added to Log ID {log_id}")
        return log
    
    # ==========================================
    # DELETE
    # ==========================================
    
    @classmethod
    def delete_log(cls, log_id: int) -> bool:
        """
        Hapus log aktivitas berdasarkan ID
        
        Args:
            log_id: ID log yang akan dihapus
        
        Returns:
            True jika berhasil, False jika gagal
        """
        log = cls.get_by_id(log_id)
        if not log:
            logger.warning(f"Log ID {log_id} not found for deletion")
            return False
        
        log_repr = str(log)
        log.delete()
        logger.info(f"Log deleted: {log_repr}")
        return True
    
    @classmethod
    def delete_old_logs(cls, days: int = 90) -> int:
        """
        Hapus log yang lebih tua dari X hari
        
        Args:
            days: Hapus log lebih tua dari X hari
        
        Returns:
            Jumlah log yang dihapus
        """
        LogAktivitas = cls.get_model()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count, _ = LogAktivitas.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Deleted {deleted_count} logs older than {days} days")
        return deleted_count
    
    @classmethod
    def delete_by_model(cls, model_name: str) -> int:
        """Hapus semua log untuk model tertentu"""
        LogAktivitas = cls.get_model()
        deleted_count, _ = LogAktivitas.objects.filter(
            model_name=model_name
        ).delete()
        
        logger.info(f"Deleted {deleted_count} logs for model {model_name}")
        return deleted_count
    
    @classmethod
    def clear_all_logs(cls) -> int:
        """Hapus semua log (gunakan dengan hati-hati!)"""
        LogAktivitas = cls.get_model()
        count = LogAktivitas.objects.count()
        LogAktivitas.objects.all().delete()
        
        logger.warning(f"All {count} logs have been cleared!")
        return count
    
    # ==========================================
    # TRACKING PERUBAHAN FIELD
    # ==========================================
    
    @classmethod
    def cache_pre_save_data(cls, instance: models.Model):
        """
        Simpan data sebelum save untuk tracking perubahan
        Dipanggil dari pre_save signal
        """
        if not instance.pk:
            return  # Skip untuk object baru
        
        model_name = instance.__class__.__name__
        cache_key = f"{model_name}_{instance.pk}"
        
        try:
            # Ambil data lama dari database
            old_instance = instance.__class__.objects.get(pk=instance.pk)
            
            # Simpan semua field values
            old_data = {}
            for field in instance._meta.fields:
                field_name = field.name
                if field_name not in ['created_at', 'updated_at']:
                    old_data[field_name] = getattr(old_instance, field_name)
            
            cls._pre_save_cache[cache_key] = old_data
            
        except instance.__class__.DoesNotExist:
            pass
    
    @classmethod
    def get_field_changes(cls, instance: models.Model) -> Dict[str, Dict]:
        """
        Bandingkan data baru dengan cache untuk mendapatkan perubahan
        
        Returns:
            Dict dengan format: {field_name: {'old': value, 'new': value}}
        """
        model_name = instance.__class__.__name__
        cache_key = f"{model_name}_{instance.pk}"
        
        if cache_key not in cls._pre_save_cache:
            return {}
        
        old_data = cls._pre_save_cache.pop(cache_key)  # Pop to clear cache
        changes = {}
        
        for field in instance._meta.fields:
            field_name = field.name
            if field_name in ['created_at', 'updated_at']:
                continue
            
            old_value = old_data.get(field_name)
            new_value = getattr(instance, field_name)
            
            # Convert untuk comparison
            if isinstance(old_value, models.Model):
                old_value = old_value.pk if old_value else None
            if isinstance(new_value, models.Model):
                new_value = new_value.pk if new_value else None
            
            if old_value != new_value:
                changes[field_name] = {
                    'old': str(old_value) if old_value is not None else 'None',
                    'new': str(new_value) if new_value is not None else 'None'
                }
        
        return changes
    
    @classmethod
    def format_changes(cls, changes: Dict[str, Dict]) -> str:
        """Format perubahan menjadi string yang readable"""
        if not changes:
            return "Tidak ada perubahan"
        
        lines = []
        for field, values in changes.items():
            lines.append(f"• {field}: '{values['old']}' → '{values['new']}'")
        
        return "\n".join(lines)
    
    # ==========================================
    # STATISTIK
    # ==========================================
    
    @classmethod
    def get_statistics(cls, days: int = 30) -> Dict[str, Any]:
        """Dapatkan statistik log aktivitas"""
        LogAktivitas = cls.get_model()
        since = datetime.now() - timedelta(days=days)
        
        logs = LogAktivitas.objects.filter(created_at__gte=since)
        
        # Count per aksi
        aksi_counts = {}
        for aksi_choice in ['create', 'update', 'delete', 'view', 'login', 'logout']:
            aksi_counts[aksi_choice] = logs.filter(aksi=aksi_choice).count()
        
        # Count per model
        model_counts = {}
        for log in logs.values('model_name').distinct():
            model_name = log['model_name']
            model_counts[model_name] = logs.filter(model_name=model_name).count()
        
        # Count per user
        user_counts = {}
        for log in logs.values('user').distinct():
            user = log['user']
            user_counts[user] = logs.filter(user=user).count()
        
        return {
            'period_days': days,
            'total_logs': logs.count(),
            'by_aksi': aksi_counts,
            'by_model': model_counts,
            'by_user': user_counts,
            'generated_at': datetime.now().isoformat()
        }
    
    @classmethod
    def get_activity_summary(cls) -> str:
        """Generate ringkasan aktivitas dalam format text"""
        stats = cls.get_statistics(30)
        
        lines = [
            "=" * 50,
            "📊 RINGKASAN LOG AKTIVITAS (30 Hari Terakhir)",
            "=" * 50,
            f"Total Log: {stats['total_logs']}",
            "",
            "Berdasarkan Aksi:",
        ]
        
        aksi_icons = {
            'create': '➕',
            'update': '✏️',
            'delete': '🗑️',
            'view': '👁️',
            'login': '🔓',
            'logout': '🔒'
        }
        
        for aksi, count in stats['by_aksi'].items():
            icon = aksi_icons.get(aksi, '•')
            lines.append(f"  {icon} {aksi.capitalize()}: {count}")
        
        lines.append("")
        lines.append("Berdasarkan Model:")
        for model, count in stats['by_model'].items():
            lines.append(f"  📦 {model}: {count}")
        
        lines.append("")
        lines.append("Berdasarkan User:")
        for user, count in stats['by_user'].items():
            lines.append(f"  👤 {user}: {count}")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    # ==========================================
    # EXPORT
    # ==========================================
    
    @classmethod
    def export_to_json(cls, filepath: str = None, days: int = 30) -> str:
        """Export log ke file JSON"""
        LogAktivitas = cls.get_model()
        since = datetime.now() - timedelta(days=days)
        
        logs = LogAktivitas.objects.filter(created_at__gte=since)
        
        data = {
            'exported_at': datetime.now().isoformat(),
            'period_days': days,
            'total_logs': logs.count(),
            'logs': []
        }
        
        for log in logs:
            data['logs'].append({
                'id': log.id,
                'user': log.user,
                'aksi': log.aksi,
                'model_name': log.model_name,
                'object_id': log.object_id,
                'object_repr': log.object_repr,
                'perubahan': log.perubahan,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat() if log.created_at else None
            })
        
        if not filepath:
            filepath = f"logs/log_aktivitas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Logs exported to {filepath}")
        return filepath


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def log_create(instance: models.Model, user: str = 'system', request=None):
    """Helper untuk log CREATE"""
    ip = None
    user_agent = ''
    
    if request:
        ip = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    LogAktivitasService.create_log(
        aksi='create',
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        object_repr=str(instance),
        user=user,
        ip_address=ip,
        user_agent=user_agent
    )


def log_update(instance: models.Model, changes: Dict, user: str = 'system', request=None):
    """Helper untuk log UPDATE dengan detail perubahan"""
    ip = None
    user_agent = ''
    
    if request:
        ip = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    perubahan = LogAktivitasService.format_changes(changes)
    
    LogAktivitasService.create_log(
        aksi='update',
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        object_repr=str(instance),
        perubahan=perubahan,
        user=user,
        ip_address=ip,
        user_agent=user_agent
    )


def log_delete(instance: models.Model, user: str = 'system', request=None):
    """Helper untuk log DELETE"""
    ip = None
    user_agent = ''
    
    if request:
        ip = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Simpan semua data sebelum dihapus
    data_backup = {}
    for field in instance._meta.fields:
        if field.name not in ['created_at', 'updated_at']:
            value = getattr(instance, field.name)
            if isinstance(value, models.Model):
                data_backup[field.name] = str(value)
            else:
                data_backup[field.name] = str(value) if value is not None else None
    
    perubahan = f"Data dihapus: {json.dumps(data_backup, ensure_ascii=False)}"
    
    LogAktivitasService.create_log(
        aksi='delete',
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        object_repr=str(instance),
        perubahan=perubahan,
        user=user,
        ip_address=ip,
        user_agent=user_agent
    )


def _get_client_ip(request):
    """Mendapatkan IP address client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
