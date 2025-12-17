"""
============================================
VERSION CONTROL SERVICE - RENTAL MOBIL
============================================
Service untuk version control data dengan fitur:
- Commit: Menyimpan snapshot data sebelum perubahan
- Rollback: Mengembalikan data ke versi sebelumnya
- History: Melihat riwayat perubahan
============================================
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Type
from django.db import models, transaction
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger('rental.version_control')


class CustomJSONEncoder(DjangoJSONEncoder):
    """Custom encoder untuk handle Decimal dan datetime"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class VersionControlService:
    """
    Service untuk mengelola version control data.
    
    Penggunaan:
        from rental.version_control import VersionControlService as VCS
        from rental.models import Mobil, DataVersion
        
        # Commit sebelum update
        mobil = Mobil.objects.get(pk=1)
        VCS.commit(mobil, 'Mengubah harga sewa', user='admin')
        
        # Rollback ke versi sebelumnya
        VCS.rollback('Mobil', object_id=1, version=2, user='admin')
        
        # Lihat history
        history = VCS.get_history('Mobil', object_id=1)
    """
    
    @staticmethod
    def _get_model_class(model_name: str):
        """Get model class dari nama model"""
        from rental.models import Mobil, Pelanggan, Penyewaan, Pembayaran
        models_map = {
            'Mobil': Mobil,
            'Pelanggan': Pelanggan,
            'Penyewaan': Penyewaan,
            'Pembayaran': Pembayaran,
        }
        return models_map.get(model_name)
    
    @staticmethod
    def _serialize_instance(instance: models.Model) -> Dict:
        """Serialize instance ke dictionary"""
        data = {}
        for field in instance._meta.fields:
            value = getattr(instance, field.name)
            
            # Handle special types
            if isinstance(value, datetime):
                data[field.name] = value.isoformat()
            elif isinstance(value, Decimal):
                data[field.name] = float(value)
            elif isinstance(value, models.Model):
                data[field.name] = value.pk
            elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                data[field.name] = list(value)
            else:
                data[field.name] = value
        
        return data
    
    @staticmethod
    def _get_next_version(model_name: str, object_id: int, branch: str = 'main') -> int:
        """Dapatkan nomor versi berikutnya"""
        from rental.models import DataVersion
        last_version = DataVersion.objects.filter(
            model_name=model_name,
            object_id=object_id,
            branch=branch
        ).order_by('-version').first()
        
        return (last_version.version + 1) if last_version else 1
    
    # ==========================================
    # COMMIT
    # ==========================================
    
    @staticmethod
    def commit(
        instance: models.Model,
        message: str = '',
        user: str = 'system',
        action: str = 'commit',
        branch: str = 'main'
    ):
        """
        Commit snapshot data saat ini.
        
        Args:
            instance: Model instance yang akan di-commit
            message: Pesan commit
            user: Username yang melakukan commit
            action: 'create', 'update', 'delete', atau 'commit'
            branch: Nama branch (default: 'main')
        
        Returns:
            DataVersion instance
        """
        from rental.models import DataVersion
        
        model_name = instance.__class__.__name__
        object_id = instance.pk or 0
        
        # Serialize data saat ini
        data_snapshot = VersionControlService._serialize_instance(instance)
        
        # Dapatkan versi sebelumnya
        previous_version = DataVersion.objects.filter(
            model_name=model_name,
            object_id=object_id,
            branch=branch,
            is_current=True
        ).first()
        
        # Set semua versi sebelumnya sebagai bukan current
        DataVersion.objects.filter(
            model_name=model_name,
            object_id=object_id,
            branch=branch,
            is_current=True
        ).update(is_current=False)
        
        # Buat versi baru
        version = DataVersion.objects.create(
            model_name=model_name,
            object_id=object_id,
            version=VersionControlService._get_next_version(model_name, object_id, branch),
            data_snapshot=data_snapshot,
            action=action,
            created_by=user,
            commit_message=message,
            parent_version=previous_version,
            branch=branch,
            is_current=True
        )
        
        logger.info(f"Commit: {model_name}#{object_id} v{version.version} [{branch}] - {message}")
        return version
    
    @staticmethod
    def commit_create(instance: models.Model, message: str = '', user: str = 'system'):
        """Shortcut untuk commit CREATE"""
        return VersionControlService.commit(
            instance, 
            message=message or 'Data baru dibuat', 
            user=user, 
            action='create'
        )
    
    @staticmethod
    def commit_update(instance: models.Model, message: str = '', user: str = 'system'):
        """Shortcut untuk commit UPDATE"""
        return VersionControlService.commit(
            instance, 
            message=message or 'Data diupdate', 
            user=user, 
            action='update'
        )
    
    @staticmethod
    def commit_delete(instance: models.Model, message: str = '', user: str = 'system'):
        """Shortcut untuk commit DELETE"""
        return VersionControlService.commit(
            instance, 
            message=message or 'Data dihapus', 
            user=user, 
            action='delete'
        )
    
    # ==========================================
    # ROLLBACK
    # ==========================================
    
    @staticmethod
    def rollback(
        model_name: str,
        object_id: int,
        version: int = None,
        user: str = 'system',
        branch: str = 'main'
    ):
        """
        Rollback data ke versi tertentu.
        
        Args:
            model_name: Nama model (e.g., 'Mobil', 'Pelanggan')
            object_id: ID objek yang akan di-rollback
            version: Nomor versi target (default: versi sebelumnya)
            user: Username yang melakukan rollback
            branch: Nama branch
        
        Returns:
            Model instance yang sudah di-rollback, atau None jika gagal
        """
        from rental.models import DataVersion
        
        model_class = VersionControlService._get_model_class(model_name)
        if not model_class:
            logger.error(f"Rollback gagal: Model {model_name} tidak ditemukan")
            return None
        
        # Cari versi target
        if version:
            target_version = DataVersion.objects.filter(
                model_name=model_name,
                object_id=object_id,
                version=version,
                branch=branch
            ).first()
        else:
            # Ambil versi sebelum current
            current = DataVersion.objects.filter(
                model_name=model_name,
                object_id=object_id,
                branch=branch,
                is_current=True
            ).first()
            
            if current and current.parent_version:
                target_version = current.parent_version
            else:
                logger.warning(f"Rollback gagal: Tidak ada versi sebelumnya untuk {model_name}#{object_id}")
                return None
        
        if not target_version:
            logger.warning(f"Rollback gagal: Versi {version} tidak ditemukan untuk {model_name}#{object_id}")
            return None
        
        # Ambil data dari versi target
        target_data = target_version.get_data()
        
        if not target_data:
            logger.warning(f"Rollback gagal: Data tidak valid untuk {model_name}#{object_id} v{version}")
            return None
        
        try:
            with transaction.atomic():
                # Cek apakah objek masih ada
                try:
                    instance = model_class.objects.get(pk=object_id)
                except model_class.DoesNotExist:
                    # Objek sudah dihapus, buat baru dengan ID sama
                    instance = model_class(id=object_id)
                
                # Update field dari target_data
                for field_name, value in target_data.items():
                    if field_name in ['id', 'created_at', 'updated_at']:
                        continue
                    if hasattr(instance, field_name):
                        try:
                            setattr(instance, field_name, value)
                        except Exception:
                            pass  # Skip jika field tidak bisa di-set
                
                # Simpan
                instance.save()
                
                # Commit rollback sebagai versi baru
                VersionControlService.commit(
                    instance,
                    message=f'Rollback ke versi {target_version.version}',
                    user=user,
                    action='rollback',
                    branch=branch
                )
                
                logger.info(f"Rollback berhasil: {model_name}#{object_id} ke v{target_version.version}")
                return instance
                
        except Exception as e:
            logger.error(f"Rollback error: {str(e)}")
            return None
    
    # ==========================================
    # HISTORY
    # ==========================================
    
    @staticmethod
    def get_history(
        model_name: str,
        object_id: int,
        branch: str = 'main',
        limit: int = 50
    ) -> List:
        """Dapatkan riwayat versi untuk objek tertentu"""
        from rental.models import DataVersion
        return list(DataVersion.objects.filter(
            model_name=model_name,
            object_id=object_id,
            branch=branch
        ).order_by('-version')[:limit])
    
    @staticmethod
    def get_current_version(model_name: str, object_id: int, branch: str = 'main'):
        """Dapatkan versi aktif saat ini"""
        from rental.models import DataVersion
        return DataVersion.objects.filter(
            model_name=model_name,
            object_id=object_id,
            branch=branch,
            is_current=True
        ).first()
    
    @staticmethod
    def get_version(model_name: str, object_id: int, version: int, branch: str = 'main'):
        """Dapatkan versi tertentu"""
        from rental.models import DataVersion
        return DataVersion.objects.filter(
            model_name=model_name,
            object_id=object_id,
            version=version,
            branch=branch
        ).first()
    
    @staticmethod
    def compare_versions(version1, version2) -> Dict[str, Dict]:
        """
        Bandingkan dua versi DataVersion dan dapatkan perbedaannya.
        
        Args:
            version1: DataVersion instance pertama
            version2: DataVersion instance kedua
        
        Returns:
            Dict dengan format: {field: {'v1': value, 'v2': value}}
        """
        data1 = version1.get_data() if version1 else {}
        data2 = version2.get_data() if version2 else {}
        
        diff = {}
        all_keys = set(data1.keys()) | set(data2.keys())
        
        for key in all_keys:
            if key in ['id', 'created_at', 'updated_at']:
                continue
            val1 = data1.get(key)
            val2 = data2.get(key)
            if val1 != val2:
                diff[key] = {'v1': val1, 'v2': val2}
        
        return diff
    
    # ==========================================
    # BRANCH MANAGEMENT
    # ==========================================
    
    @staticmethod
    def create_branch(
        model_name: str,
        object_id: int,
        branch_name: str,
        from_branch: str = 'main',
        user: str = 'system'
    ):
        """Buat branch baru dari branch yang ada"""
        from rental.models import DataVersion
        
        # Dapatkan versi current dari source branch
        source_version = DataVersion.objects.filter(
            model_name=model_name,
            object_id=object_id,
            branch=from_branch,
            is_current=True
        ).first()
        
        if not source_version:
            logger.error(f"Create branch gagal: Versi sumber tidak ditemukan")
            return None
        
        # Buat versi pertama di branch baru
        new_version = DataVersion.objects.create(
            model_name=model_name,
            object_id=object_id,
            version=1,
            data_snapshot=source_version.data_snapshot,
            action='commit',
            created_by=user,
            commit_message=f'Branch created from {from_branch} v{source_version.version}',
            parent_version=source_version,
            branch=branch_name,
            is_current=True
        )
        
        logger.info(f"Branch '{branch_name}' dibuat untuk {model_name}#{object_id}")
        return new_version
    
    @staticmethod
    def list_branches(model_name: str, object_id: int) -> List[str]:
        """Dapatkan daftar branch untuk objek tertentu"""
        from rental.models import DataVersion
        return list(DataVersion.objects.filter(
            model_name=model_name,
            object_id=object_id
        ).values_list('branch', flat=True).distinct())
    
    # ==========================================
    # UTILITY
    # ==========================================
    
    @staticmethod
    def cleanup_old_versions(keep_last: int = 10) -> int:
        """
        Hapus versi lama, simpan hanya N versi terakhir per objek per branch.
        
        Args:
            keep_last: Jumlah versi terakhir yang disimpan
        
        Returns:
            Jumlah versi yang dihapus
        """
        from rental.models import DataVersion
        
        deleted_count = 0
        
        # Dapatkan semua kombinasi model_name + object_id + branch
        objects = DataVersion.objects.values('model_name', 'object_id', 'branch').distinct()
        
        for obj in objects:
            # Dapatkan ID versi yang harus disimpan
            versions_to_keep = DataVersion.objects.filter(
                model_name=obj['model_name'],
                object_id=obj['object_id'],
                branch=obj['branch']
            ).order_by('-version')[:keep_last].values_list('id', flat=True)
            
            deleted, _ = DataVersion.objects.filter(
                model_name=obj['model_name'],
                object_id=obj['object_id'],
                branch=obj['branch']
            ).exclude(id__in=list(versions_to_keep)).delete()
            
            deleted_count += deleted
        
        logger.info(f"Cleanup: {deleted_count} versi lama dihapus")
        return deleted_count
    
    @staticmethod
    def print_history(model_name: str, object_id: int, branch: str = 'main') -> str:
        """Generate string history untuk display"""
        history = VersionControlService.get_history(model_name, object_id, branch)
        
        if not history:
            return f"Tidak ada history untuk {model_name}#{object_id} [{branch}]"
        
        lines = [
            "=" * 60,
            f"📜 HISTORY: {model_name}#{object_id} [{branch}]",
            "=" * 60,
        ]
        
        action_icons = {
            'create': '➕',
            'update': '✏️',
            'delete': '🗑️',
            'commit': '📝',
            'rollback': '↩️'
        }
        
        for v in history:
            icon = action_icons.get(v.action, '•')
            current = ' [CURRENT]' if v.is_current else ''
            
            lines.append(f"\nv{v.version}{current}")
            lines.append(f"  {icon} {v.get_action_display()}: {v.commit_message}")
            lines.append(f"  👤 {v.created_by} | 🕐 {v.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show changes from parent
            if v.parent_version:
                changes = v.get_changes_from_parent()
                if changes and not changes.get('new'):
                    lines.append("  📝 Perubahan:")
                    for field, vals in changes.items():
                        if isinstance(vals, dict) and 'old' in vals and 'new' in vals:
                            lines.append(f"     • {field}: {vals['old']} → {vals['new']}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


# Shortcut alias
VCS = VersionControlService


# ==========================================
# CLI INTERFACE
# ==========================================
if __name__ == '__main__':
    import os
    import sys
    import django
    
    # Setup Django
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_mobil_web.settings')
    django.setup()
    
    from rental.models import Mobil, Pelanggan, DataVersion
    
    print("=" * 60)
    print("🔄 VERSION CONTROL SYSTEM - RENTAL MOBIL")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("""
Penggunaan:
  python version_control.py history <model> <id>     - Lihat history versi
  python version_control.py rollback <model> <id> <version> - Rollback ke versi
  python version_control.py cleanup [keep=10]        - Bersihkan versi lama
  python version_control.py stats                    - Statistik version control
  
Contoh:
  python version_control.py history Mobil 1
  python version_control.py rollback Mobil 1 2
  python version_control.py cleanup 5
        """)
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'history':
        if len(sys.argv) < 4:
            print("Error: Butuh <model> dan <id>")
            sys.exit(1)
        model_name = sys.argv[2]
        object_id = int(sys.argv[3])
        print(VCS.print_history(model_name, object_id))
        
    elif command == 'rollback':
        if len(sys.argv) < 5:
            print("Error: Butuh <model>, <id>, dan <version>")
            sys.exit(1)
        model_name = sys.argv[2]
        object_id = int(sys.argv[3])
        version = int(sys.argv[4])
        
        result = VCS.rollback(model_name, object_id, version, user='cli')
        if result:
            print(f"✅ Berhasil rollback {model_name}#{object_id} ke versi {version}")
        else:
            print(f"❌ Gagal rollback")
            
    elif command == 'cleanup':
        keep = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        deleted = VCS.cleanup_old_versions(keep_last=keep)
        print(f"🗑️ {deleted} versi lama dihapus (keep last {keep})")
        
    elif command == 'stats':
        total = DataVersion.objects.count()
        by_model = DataVersion.objects.values('model_name').annotate(
            count=models.Count('id')
        )
        by_action = DataVersion.objects.values('action').annotate(
            count=models.Count('id')
        )
        
        print(f"\n📊 STATISTIK VERSION CONTROL")
        print(f"   Total versi: {total}")
        print(f"\n   Per Model:")
        for item in by_model:
            print(f"   - {item['model_name']}: {item['count']}")
        print(f"\n   Per Aksi:")
        for item in by_action:
            print(f"   - {item['action']}: {item['count']}")
    
    else:
        print(f"Command tidak dikenal: {command}")
