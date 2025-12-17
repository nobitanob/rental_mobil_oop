"""
============================================
PEMANTAUAN PERFORMA MODUL - RENTAL MOBIL
============================================
File ini berisi tools untuk memantau performa
setiap modul/fungsi dalam aplikasi rental mobil.

Fitur:
1. Pengukuran waktu eksekusi fungsi
2. Monitoring penggunaan memori
3. Statistik query database
4. Laporan performa modul
============================================
"""

import time
import functools
import tracemalloc
from datetime import datetime
from typing import Callable, Dict, List, Any, Optional
from collections import defaultdict
import threading
import json
import os


class PerformanceMonitor:
    """
    Kelas untuk memantau performa modul/fungsi.
    Singleton pattern untuk memastikan satu instance global.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.metrics: Dict[str, List[Dict]] = defaultdict(list)
        self.active_monitors: Dict[str, float] = {}
        self.memory_tracking = False
        self.log_file = "logs/performance_log.json"
        
        # Buat folder logs jika belum ada
        os.makedirs("logs", exist_ok=True)
    
    def start_timer(self, name: str) -> None:
        """Mulai timer untuk operasi tertentu"""
        self.active_monitors[name] = time.perf_counter()
    
    def stop_timer(self, name: str) -> float:
        """Stop timer dan return durasi dalam ms"""
        if name not in self.active_monitors:
            return 0.0
        
        start_time = self.active_monitors.pop(name)
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        self.metrics[name].append({
            "timestamp": datetime.now().isoformat(),
            "duration_ms": round(duration_ms, 3),
            "type": "timer"
        })
        
        return duration_ms
    
    def record_metric(self, name: str, value: float, unit: str = "ms") -> None:
        """Catat metrik custom"""
        self.metrics[name].append({
            "timestamp": datetime.now().isoformat(),
            "value": value,
            "unit": unit,
            "type": "custom"
        })
    
    def get_stats(self, name: str) -> Dict[str, Any]:
        """Dapatkan statistik untuk metrik tertentu"""
        if name not in self.metrics or not self.metrics[name]:
            return {"error": f"No metrics found for {name}"}
        
        durations = [
            m.get("duration_ms", m.get("value", 0)) 
            for m in self.metrics[name]
        ]
        
        return {
            "name": name,
            "count": len(durations),
            "min_ms": round(min(durations), 3),
            "max_ms": round(max(durations), 3),
            "avg_ms": round(sum(durations) / len(durations), 3),
            "total_ms": round(sum(durations), 3),
            "last_recorded": self.metrics[name][-1]["timestamp"]
        }
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Dapatkan semua statistik"""
        return {name: self.get_stats(name) for name in self.metrics}
    
    def get_summary_report(self) -> str:
        """Generate laporan ringkasan performa"""
        report = []
        report.append("=" * 60)
        report.append("📊 LAPORAN PERFORMA MODUL - RENTAL MOBIL")
        report.append(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        all_stats = self.get_all_stats()
        
        if not all_stats:
            report.append("\n⚠️ Belum ada data performa yang tercatat.")
        else:
            # Sort by average time (slowest first)
            sorted_stats = sorted(
                all_stats.items(), 
                key=lambda x: x[1].get("avg_ms", 0), 
                reverse=True
            )
            
            report.append(f"\n{'Modul/Fungsi':<35} {'Count':>8} {'Avg(ms)':>10} {'Min':>8} {'Max':>8}")
            report.append("-" * 75)
            
            for name, stats in sorted_stats:
                if "error" not in stats:
                    # Indikator performa
                    avg = stats["avg_ms"]
                    if avg < 50:
                        indicator = "🟢"  # Fast
                    elif avg < 200:
                        indicator = "🟡"  # Medium
                    else:
                        indicator = "🔴"  # Slow
                    
                    report.append(
                        f"{indicator} {name:<32} {stats['count']:>8} "
                        f"{stats['avg_ms']:>10.2f} {stats['min_ms']:>8.2f} "
                        f"{stats['max_ms']:>8.2f}"
                    )
        
        report.append("\n" + "=" * 60)
        report.append("Legend: 🟢 <50ms | 🟡 50-200ms | 🔴 >200ms")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_to_file(self) -> str:
        """Simpan metrik ke file JSON"""
        data = {
            "generated_at": datetime.now().isoformat(),
            "metrics": dict(self.metrics),
            "summary": self.get_all_stats()
        }
        
        with open(self.log_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        return self.log_file
    
    def clear_metrics(self) -> None:
        """Hapus semua metrik"""
        self.metrics.clear()
        self.active_monitors.clear()


# Global instance
monitor = PerformanceMonitor()


def measure_time(func: Callable = None, name: str = None):
    """
    Decorator untuk mengukur waktu eksekusi fungsi.
    
    Penggunaan:
        @measure_time
        def my_function():
            pass
            
        @measure_time(name="Custom Name")
        def my_function():
            pass
    """
    def decorator(f: Callable) -> Callable:
        metric_name = name or f"{f.__module__}.{f.__qualname__}"
        
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            monitor.start_timer(metric_name)
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                duration = monitor.stop_timer(metric_name)
                # Log jika terlalu lambat (>500ms)
                if duration > 500:
                    print(f"⚠️ SLOW: {metric_name} took {duration:.2f}ms")
        
        return wrapper
    
    if func is not None:
        return decorator(func)
    return decorator


def measure_memory(func: Callable) -> Callable:
    """
    Decorator untuk mengukur penggunaan memori fungsi.
    
    Penggunaan:
        @measure_memory
        def my_function():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        metric_name = f"{func.__module__}.{func.__qualname__}_memory"
        
        tracemalloc.start()
        try:
            result = func(*args, **kwargs)
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Record in KB
            monitor.record_metric(metric_name, peak / 1024, "KB")
            
            return result
        except Exception as e:
            tracemalloc.stop()
            raise e
    
    return wrapper


class DatabaseQueryMonitor:
    """
    Context manager untuk memantau query database Django.
    
    Penggunaan:
        with DatabaseQueryMonitor("get_all_mobil"):
            mobils = Mobil.objects.all()
    """
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.query_count_start = 0
    
    def __enter__(self):
        from django.db import connection
        self.start_time = time.perf_counter()
        self.query_count_start = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        from django.db import connection
        
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        query_count = len(connection.queries) - self.query_count_start
        
        monitor.record_metric(f"{self.name}_time", duration_ms, "ms")
        monitor.record_metric(f"{self.name}_queries", query_count, "count")
        
        # Warning jika terlalu banyak query (N+1 problem)
        if query_count > 10:
            print(f"⚠️ WARNING: {self.name} executed {query_count} queries!")
        
        return False


# ============================================
# CONTOH PENGGUNAAN UNTUK MODUL RENTAL
# ============================================

@measure_time(name="mobil.get_available")
def get_available_mobil():
    """Contoh: Ambil mobil yang tersedia"""
    from rental.models import Mobil
    return list(Mobil.objects.filter(status='tersedia'))


@measure_time(name="pelanggan.search")
def search_pelanggan(keyword: str):
    """Contoh: Cari pelanggan"""
    from rental.models import Pelanggan
    return list(Pelanggan.objects.filter(nama__icontains=keyword))


@measure_time(name="penyewaan.create")
def create_penyewaan(mobil_id: int, pelanggan_id: int, tanggal_sewa, tanggal_kembali):
    """Contoh: Buat penyewaan baru"""
    from rental.models import Penyewaan, Mobil, Pelanggan
    
    mobil = Mobil.objects.get(id=mobil_id)
    pelanggan = Pelanggan.objects.get(id=pelanggan_id)
    
    penyewaan = Penyewaan(
        mobil=mobil,
        pelanggan=pelanggan,
        tanggal_sewa=tanggal_sewa,
        tanggal_kembali=tanggal_kembali
    )
    penyewaan.save()
    return penyewaan


@measure_time(name="pembayaran.process")
def process_pembayaran(penyewaan_id: int, jumlah: float, metode: str):
    """Contoh: Proses pembayaran"""
    from rental.models import Pembayaran, Penyewaan
    
    penyewaan = Penyewaan.objects.get(id=penyewaan_id)
    
    pembayaran = Pembayaran(
        penyewaan=penyewaan,
        jumlah=jumlah,
        metode_pembayaran=metode,
        status='pending'
    )
    pembayaran.save()
    return pembayaran


# ============================================
# CLI UNTUK MELIHAT PERFORMA
# ============================================

def print_performance_report():
    """Print laporan performa ke console"""
    print(monitor.get_summary_report())


def run_benchmark():
    """Jalankan benchmark untuk semua modul"""
    print("🔄 Menjalankan benchmark modul...")
    print("-" * 40)
    
    try:
        # Test get available mobil
        print("Testing: get_available_mobil...")
        for _ in range(5):
            get_available_mobil()
        
        # Test search pelanggan
        print("Testing: search_pelanggan...")
        for keyword in ["budi", "andi", "test", "a", "e"]:
            search_pelanggan(keyword)
        
        print("\n✅ Benchmark selesai!")
        print_performance_report()
        
        # Save to file
        filepath = monitor.save_to_file()
        print(f"\n📁 Hasil disimpan ke: {filepath}")
        
    except Exception as e:
        print(f"❌ Error saat benchmark: {e}")


if __name__ == "__main__":
    import sys
    
    # Setup Django
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_mobil_web.settings')
    
    try:
        django.setup()
    except Exception as e:
        print(f"⚠️ Django setup error: {e}")
        print("Pastikan menjalankan dari folder rental_mobil_web")
        sys.exit(1)
    
    print("=" * 50)
    print("🔧 PERFORMANCE MONITOR - RENTAL MOBIL")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "benchmark":
            run_benchmark()
        elif command == "report":
            print_performance_report()
        elif command == "clear":
            monitor.clear_metrics()
            print("✅ Metrics cleared")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: benchmark, report, clear")
    else:
        print("\nUsage:")
        print("  python performance_monitor.py benchmark  - Run benchmark")
        print("  python performance_monitor.py report     - Show report")
        print("  python performance_monitor.py clear      - Clear metrics")
