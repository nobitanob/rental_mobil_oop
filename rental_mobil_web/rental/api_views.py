"""
REST API Views untuk Rental Mobil
Endpoints untuk testing dengan Postman
"""
import json
from datetime import datetime, date, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
from .models import Mobil, Pelanggan, Penyewaan, Pembayaran


# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════
def api_response(success: bool, data=None, message: str = "", status: int = 200):
    """Standard API response format"""
    return JsonResponse({
        "success": success,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }, status=status)


def parse_json_body(request):
    """Parse JSON body from request"""
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return None


# ══════════════════════════════════════════════════════════════
# MOBIL API ENDPOINTS
# ══════════════════════════════════════════════════════════════
@csrf_exempt
@require_http_methods(["GET", "POST"])
def mobil_list(request):
    """
    GET: Daftar semua mobil
    POST: Tambah mobil baru
    """
    if request.method == "GET":
        # Filter by status (optional)
        status_filter = request.GET.get('status', None)
        
        if status_filter:
            mobils = Mobil.objects.filter(status=status_filter)
        else:
            mobils = Mobil.objects.all()
        
        data = [{
            "id": m.id,
            "merk": m.merk,
            "model": m.model,
            "tahun": m.tahun,
            "plat_nomor": m.plat_nomor,
            "harga_sewa_per_hari": float(m.harga_sewa_per_hari),
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in mobils]
        
        return api_response(True, data, f"Ditemukan {len(data)} mobil")
    
    elif request.method == "POST":
        body = parse_json_body(request)
        if not body:
            return api_response(False, None, "Invalid JSON body", 400)
        
        try:
            mobil = Mobil.objects.create(
                merk=body.get('merk'),
                model=body.get('model'),
                tahun=body.get('tahun'),
                plat_nomor=body.get('plat_nomor'),
                harga_sewa_per_hari=body.get('harga_sewa_per_hari'),
                status=body.get('status', 'tersedia')
            )
            
            return api_response(True, {
                "id": mobil.id,
                "merk": mobil.merk,
                "model": mobil.model
            }, "Mobil berhasil ditambahkan", 201)
            
        except Exception as e:
            return api_response(False, None, str(e), 400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def mobil_detail(request, id):
    """
    GET: Detail mobil by ID
    PUT: Update mobil
    DELETE: Hapus mobil
    """
    try:
        mobil = Mobil.objects.get(id=id)
    except Mobil.DoesNotExist:
        return api_response(False, None, "Mobil tidak ditemukan", 404)
    
    if request.method == "GET":
        data = {
            "id": mobil.id,
            "merk": mobil.merk,
            "model": mobil.model,
            "tahun": mobil.tahun,
            "plat_nomor": mobil.plat_nomor,
            "harga_sewa_per_hari": float(mobil.harga_sewa_per_hari),
            "status": mobil.status,
            "created_at": mobil.created_at.isoformat() if mobil.created_at else None,
            "updated_at": mobil.updated_at.isoformat() if mobil.updated_at else None
        }
        return api_response(True, data, "Detail mobil")
    
    elif request.method == "PUT":
        body = parse_json_body(request)
        if not body:
            return api_response(False, None, "Invalid JSON body", 400)
        
        try:
            mobil.merk = body.get('merk', mobil.merk)
            mobil.model = body.get('model', mobil.model)
            mobil.tahun = body.get('tahun', mobil.tahun)
            mobil.plat_nomor = body.get('plat_nomor', mobil.plat_nomor)
            mobil.harga_sewa_per_hari = body.get('harga_sewa_per_hari', mobil.harga_sewa_per_hari)
            mobil.status = body.get('status', mobil.status)
            mobil.save()
            
            return api_response(True, {"id": mobil.id}, "Mobil berhasil diupdate")
        except Exception as e:
            return api_response(False, None, str(e), 400)
    
    elif request.method == "DELETE":
        mobil.delete()
        return api_response(True, None, "Mobil berhasil dihapus")


# ══════════════════════════════════════════════════════════════
# PELANGGAN API ENDPOINTS
# ══════════════════════════════════════════════════════════════
@csrf_exempt
@require_http_methods(["GET", "POST"])
def pelanggan_list(request):
    """
    GET: Daftar semua pelanggan
    POST: Tambah pelanggan baru
    """
    if request.method == "GET":
        pelanggans = Pelanggan.objects.all()
        
        data = [{
            "id": p.id,
            "nik": p.nik,
            "nama": p.nama,
            "alamat": p.alamat,
            "no_telepon": p.no_telepon,
            "email": p.email,
            "created_at": p.created_at.isoformat() if p.created_at else None
        } for p in pelanggans]
        
        return api_response(True, data, f"Ditemukan {len(data)} pelanggan")
    
    elif request.method == "POST":
        body = parse_json_body(request)
        if not body:
            return api_response(False, None, "Invalid JSON body", 400)
        
        try:
            pelanggan = Pelanggan.objects.create(
                nik=body.get('nik'),
                nama=body.get('nama'),
                alamat=body.get('alamat', ''),
                no_telepon=body.get('no_telepon', ''),
                email=body.get('email', '')
            )
            
            return api_response(True, {
                "id": pelanggan.id,
                "nik": pelanggan.nik,
                "nama": pelanggan.nama
            }, "Pelanggan berhasil ditambahkan", 201)
            
        except Exception as e:
            return api_response(False, None, str(e), 400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def pelanggan_detail(request, id):
    """
    GET: Detail pelanggan by ID
    PUT: Update pelanggan
    DELETE: Hapus pelanggan
    """
    try:
        pelanggan = Pelanggan.objects.get(id=id)
    except Pelanggan.DoesNotExist:
        return api_response(False, None, "Pelanggan tidak ditemukan", 404)
    
    if request.method == "GET":
        data = {
            "id": pelanggan.id,
            "nik": pelanggan.nik,
            "nama": pelanggan.nama,
            "alamat": pelanggan.alamat,
            "no_telepon": pelanggan.no_telepon,
            "email": pelanggan.email,
            "created_at": pelanggan.created_at.isoformat() if pelanggan.created_at else None
        }
        return api_response(True, data, "Detail pelanggan")
    
    elif request.method == "PUT":
        body = parse_json_body(request)
        if not body:
            return api_response(False, None, "Invalid JSON body", 400)
        
        try:
            pelanggan.nama = body.get('nama', pelanggan.nama)
            pelanggan.alamat = body.get('alamat', pelanggan.alamat)
            pelanggan.no_telepon = body.get('no_telepon', pelanggan.no_telepon)
            pelanggan.email = body.get('email', pelanggan.email)
            pelanggan.save()
            
            return api_response(True, {"id": pelanggan.id}, "Pelanggan berhasil diupdate")
        except Exception as e:
            return api_response(False, None, str(e), 400)
    
    elif request.method == "DELETE":
        pelanggan.delete()
        return api_response(True, None, "Pelanggan berhasil dihapus")


# ══════════════════════════════════════════════════════════════
# PENYEWAAN API ENDPOINTS
# ══════════════════════════════════════════════════════════════
@csrf_exempt
@require_http_methods(["GET", "POST"])
def penyewaan_list(request):
    """
    GET: Daftar semua penyewaan
    POST: Buat penyewaan baru (sewa mobil)
    """
    if request.method == "GET":
        status_filter = request.GET.get('status', None)
        
        penyewaans = Penyewaan.objects.select_related('mobil', 'pelanggan').all()
        if status_filter:
            penyewaans = penyewaans.filter(status=status_filter)
        
        data = [{
            "id": p.id,
            "kode_penyewaan": p.kode_penyewaan,
            "mobil": {
                "id": p.mobil.id,
                "nama": f"{p.mobil.merk} {p.mobil.model}",
                "plat_nomor": p.mobil.plat_nomor
            },
            "pelanggan": {
                "id": p.pelanggan.id,
                "nama": p.pelanggan.nama
            },
            "tanggal_sewa": p.tanggal_sewa.isoformat(),
            "tanggal_kembali": p.tanggal_kembali.isoformat(),
            "total_hari": p.total_hari,
            "total_biaya": float(p.total_biaya),
            "denda": float(p.denda) if p.denda else 0,
            "status": p.status
        } for p in penyewaans]
        
        return api_response(True, data, f"Ditemukan {len(data)} penyewaan")
    
    elif request.method == "POST":
        body = parse_json_body(request)
        if not body:
            return api_response(False, None, "Invalid JSON body", 400)
        
        try:
            # Validasi mobil
            mobil = Mobil.objects.get(id=body.get('mobil_id'))
            if mobil.status != 'tersedia':
                return api_response(False, None, f"Mobil sedang {mobil.status}", 400)
            
            # Validasi pelanggan
            pelanggan = Pelanggan.objects.get(id=body.get('pelanggan_id'))
            
            # Parse tanggal
            tanggal_sewa = datetime.strptime(body.get('tanggal_sewa'), '%Y-%m-%d').date()
            jumlah_hari = body.get('jumlah_hari', 1)
            tanggal_kembali = tanggal_sewa + timedelta(days=jumlah_hari)
            
            # Hitung biaya
            total_biaya = mobil.harga_sewa_per_hari * jumlah_hari
            
            # Generate kode
            from datetime import datetime as dt
            year_month = dt.now().strftime('%Y%m')
            last_penyewaan = Penyewaan.objects.order_by('-id').first()
            seq = (last_penyewaan.id + 1) if last_penyewaan else 1
            kode_penyewaan = f"RENT-{year_month}-{seq:04d}"
            
            # Buat penyewaan
            penyewaan = Penyewaan.objects.create(
                mobil=mobil,
                pelanggan=pelanggan,
                kode_penyewaan=kode_penyewaan,
                tanggal_sewa=tanggal_sewa,
                tanggal_kembali=tanggal_kembali,
                total_hari=jumlah_hari,
                total_biaya=total_biaya,
                status='aktif'
            )
            
            # Update status mobil
            mobil.status = 'disewa'
            mobil.save()
            
            return api_response(True, {
                "id": penyewaan.id,
                "kode_penyewaan": kode_penyewaan,
                "total_biaya": float(total_biaya),
                "tanggal_kembali": tanggal_kembali.isoformat()
            }, "Penyewaan berhasil dibuat", 201)
            
        except Mobil.DoesNotExist:
            return api_response(False, None, "Mobil tidak ditemukan", 404)
        except Pelanggan.DoesNotExist:
            return api_response(False, None, "Pelanggan tidak ditemukan", 404)
        except Exception as e:
            return api_response(False, None, str(e), 400)


@csrf_exempt
@require_http_methods(["GET"])
def penyewaan_detail(request, id):
    """GET: Detail penyewaan by ID"""
    try:
        p = Penyewaan.objects.select_related('mobil', 'pelanggan').get(id=id)
    except Penyewaan.DoesNotExist:
        return api_response(False, None, "Penyewaan tidak ditemukan", 404)
    
    data = {
        "id": p.id,
        "kode_penyewaan": p.kode_penyewaan,
        "mobil": {
            "id": p.mobil.id,
            "merk": p.mobil.merk,
            "model": p.mobil.model,
            "plat_nomor": p.mobil.plat_nomor,
            "harga_per_hari": float(p.mobil.harga_sewa_per_hari)
        },
        "pelanggan": {
            "id": p.pelanggan.id,
            "nik": p.pelanggan.nik,
            "nama": p.pelanggan.nama,
            "no_telepon": p.pelanggan.no_telepon
        },
        "tanggal_sewa": p.tanggal_sewa.isoformat(),
        "tanggal_kembali": p.tanggal_kembali.isoformat(),
        "tanggal_pengembalian": p.tanggal_pengembalian.isoformat() if p.tanggal_pengembalian else None,
        "total_hari": p.total_hari,
        "total_biaya": float(p.total_biaya),
        "denda": float(p.denda) if p.denda else 0,
        "status": p.status,
        "created_at": p.created_at.isoformat() if p.created_at else None
    }
    
    return api_response(True, data, "Detail penyewaan")


@csrf_exempt
@require_http_methods(["POST"])
def penyewaan_kembalikan(request, id):
    """POST: Proses pengembalian mobil"""
    try:
        penyewaan = Penyewaan.objects.select_related('mobil').get(id=id)
    except Penyewaan.DoesNotExist:
        return api_response(False, None, "Penyewaan tidak ditemukan", 404)
    
    if penyewaan.status != 'aktif':
        return api_response(False, None, f"Penyewaan sudah {penyewaan.status}", 400)
    
    body = parse_json_body(request)
    
    try:
        # Parse tanggal pengembalian
        if body and body.get('tanggal_pengembalian'):
            tanggal_pengembalian = datetime.strptime(
                body.get('tanggal_pengembalian'), '%Y-%m-%d'
            ).date()
        else:
            tanggal_pengembalian = date.today()
        
        # Hitung keterlambatan
        hari_keterlambatan = max(0, (tanggal_pengembalian - penyewaan.tanggal_kembali).days)
        
        # Hitung denda (1.5x harga per hari)
        denda = 0
        status = 'selesai'
        if hari_keterlambatan > 0:
            denda = float(penyewaan.mobil.harga_sewa_per_hari) * hari_keterlambatan * 1.5
            status = 'terlambat'
        
        # Update penyewaan
        penyewaan.tanggal_pengembalian = tanggal_pengembalian
        penyewaan.denda = denda
        penyewaan.status = status
        penyewaan.save()
        
        # Update status mobil
        penyewaan.mobil.status = 'tersedia'
        penyewaan.mobil.save()
        
        total_bayar = float(penyewaan.total_biaya) + denda
        
        return api_response(True, {
            "id": penyewaan.id,
            "kode_penyewaan": penyewaan.kode_penyewaan,
            "hari_keterlambatan": hari_keterlambatan,
            "denda": denda,
            "total_biaya": float(penyewaan.total_biaya),
            "total_bayar": total_bayar,
            "status": status
        }, f"Pengembalian berhasil. {'Denda: Rp {:,.0f}'.format(denda) if denda > 0 else 'Tepat waktu'}")
        
    except Exception as e:
        return api_response(False, None, str(e), 400)


# ══════════════════════════════════════════════════════════════
# STATISTIK / DASHBOARD API
# ══════════════════════════════════════════════════════════════
@require_http_methods(["GET"])
def dashboard_stats(request):
    """GET: Statistik dashboard"""
    
    total_mobil = Mobil.objects.count()
    mobil_tersedia = Mobil.objects.filter(status='tersedia').count()
    mobil_disewa = Mobil.objects.filter(status='disewa').count()
    
    total_pelanggan = Pelanggan.objects.count()
    
    penyewaan_aktif = Penyewaan.objects.filter(status='aktif').count()
    penyewaan_selesai = Penyewaan.objects.filter(status='selesai').count()
    penyewaan_terlambat = Penyewaan.objects.filter(status='terlambat').count()
    
    # Total pendapatan
    from django.db.models import Sum
    total_pendapatan = Penyewaan.objects.filter(
        status__in=['selesai', 'terlambat']
    ).aggregate(total=Sum('total_biaya'))['total'] or 0
    
    total_denda = Penyewaan.objects.aggregate(total=Sum('denda'))['total'] or 0
    
    data = {
        "mobil": {
            "total": total_mobil,
            "tersedia": mobil_tersedia,
            "disewa": mobil_disewa,
            "perbaikan": total_mobil - mobil_tersedia - mobil_disewa
        },
        "pelanggan": {
            "total": total_pelanggan
        },
        "penyewaan": {
            "aktif": penyewaan_aktif,
            "selesai": penyewaan_selesai,
            "terlambat": penyewaan_terlambat
        },
        "keuangan": {
            "total_pendapatan": float(total_pendapatan),
            "total_denda": float(total_denda)
        }
    }
    
    return api_response(True, data, "Dashboard statistics")
