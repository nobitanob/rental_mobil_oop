"""
Script untuk mengecek status dan struktur database rental_mobil_db
"""

import mysql.connector
from mysql.connector import Error
import sys
from tabulate import tabulate

class DatabaseChecker:
    """Class untuk mengecek status database"""
    
    def __init__(self, host='localhost', user='root', password='', database='rental_mobil_db'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """Membuat koneksi ke database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"✅ Berhasil terhubung ke database: {self.database}")
            return True
        except Error as e:
            print(f"❌ Gagal terhubung ke database: {e}")
            if "Unknown database" in str(e):
                print(f"\n💡 Database '{self.database}' belum ada.")
                print("   Jalankan script setup terlebih dahulu:")
                print("   python database/create_database.py")
                print("   atau")
                print("   python database/setup_simple.py")
            return False
    
    def check_tables(self):
        """Mengecek tabel-tabel yang ada"""
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Cek semua tabel
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if not tables:
                print("\n❌ Tidak ada tabel di database!")
                return False
            
            print(f"\n📊 Ditemukan {len(tables)} tabel:")
            print("-" * 60)
            
            table_data = []
            for table in tables:
                table_name = list(table.values())[0]
                
                # Hitung jumlah data
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count_result = cursor.fetchone()
                row_count = count_result['count']
                
                # Dapatkan kolom
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                
                table_data.append([table_name, len(columns), row_count])
            
            # Tampilkan dalam tabel
            headers = ["Nama Tabel", "Jumlah Kolom", "Jumlah Data"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            return True
            
        except Error as e:
            print(f"❌ Error checking tables: {e}")
            return False
        finally:
            cursor.close()
    
    def check_table_structure(self):
        """Mengecek struktur detail setiap tabel"""
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\n" + "="*80)
            print("STRUKTUR DETAIL SETIAP TABEL")
            print("="*80)
            
            for table in tables:
                table_name = list(table.values())[0]
                
                print(f"\n📋 TABEL: {table_name.upper()}")
                print("-" * 80)
                
                # Dapatkan struktur tabel
                cursor.execute(f"""
                    SELECT 
                        COLUMN_NAME,
                        COLUMN_TYPE,
                        IS_NULLABLE,
                        COLUMN_KEY,
                        COLUMN_DEFAULT,
                        EXTRA
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = '{self.database}' 
                    AND TABLE_NAME = '{table_name}'
                    ORDER BY ORDINAL_POSITION
                """)
                
                columns = cursor.fetchall()
                
                column_data = []
                for col in columns:
                    column_data.append([
                        col['COLUMN_NAME'],
                        col['COLUMN_TYPE'],
                        col['IS_NULLABLE'],
                        col['COLUMN_KEY'] or '',
                        str(col['COLUMN_DEFAULT'] or 'NULL'),
                        col['EXTRA']
                    ])
                
                headers = ["Nama Kolom", "Tipe Data", "Nullable", "Key", "Default", "Extra"]
                print(tabulate(column_data, headers=headers, tablefmt="grid"))
                
                # Cek constraints
                self._check_constraints(table_name)
                
        except Error as e:
            print(f"❌ Error checking table structure: {e}")
        finally:
            cursor.close()
    
    def _check_constraints(self, table_name):
        """Mengecek constraints pada tabel"""
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Cek foreign keys
            cursor.execute(f"""
                SELECT
                    CONSTRAINT_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = '{self.database}' 
                AND TABLE_NAME = '{table_name}'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print(f"\n🔗 Foreign Keys pada tabel {table_name}:")
                fk_data = []
                for fk in foreign_keys:
                    fk_data.append([
                        fk['CONSTRAINT_NAME'],
                        fk['COLUMN_NAME'],
                        f"{fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}"
                    ])
                
                headers = ["Constraint Name", "Column", "References"]
                print(tabulate(fk_data, headers=headers, tablefmt="simple_grid"))
            
            # Cek indexes
            cursor.execute(f"SHOW INDEX FROM {table_name}")
            indexes = cursor.fetchall()
            
            if len(indexes) > 1:  # Selain PRIMARY KEY
                print(f"\n📈 Indexes pada tabel {table_name}:")
                index_data = []
                for idx in indexes:
                    if idx['Key_name'] != 'PRIMARY':
                        index_data.append([
                            idx['Key_name'],
                            idx['Column_name'],
                            'UNIQUE' if idx['Non_unique'] == 0 else 'INDEX'
                        ])
                
                if index_data:
                    headers = ["Index Name", "Column", "Type"]
                    print(tabulate(index_data, headers=headers, tablefmt="simple_grid"))
                    
        except Error as e:
            print(f"❌ Error checking constraints: {e}")
        finally:
            cursor.close()
    
    def check_data_integrity(self):
        """Mengecek integritas data"""
        cursor = self.connection.cursor(dictionary=True)
        
        print("\n" + "="*80)
        print("CEK INTEGRITAS DATA DAN RELASI")
        print("="*80)
        
        try:
            # 1. Cek mobil tanpa status valid
            cursor.execute("""
                SELECT COUNT(*) as invalid_status 
                FROM mobil 
                WHERE status NOT IN ('tersedia', 'disewa', 'perbaikan')
            """)
            result = cursor.fetchone()
            print(f"\n1. Mobil dengan status tidak valid: {result['invalid_status']}")
            
            # 2. Cek penyewaan aktif tanpa mobil
            cursor.execute("""
                SELECT COUNT(*) as orphaned_rentals
                FROM penyewaan p
                LEFT JOIN mobil m ON p.mobil_id = m.id
                WHERE p.status = 'aktif' AND m.id IS NULL
            """)
            result = cursor.fetchone()
            print(f"2. Penyewaan aktif tanpa mobil (orphaned): {result['orphaned_rentals']}")
            
            # 3. Cek penyewaan tanpa pelanggan
            cursor.execute("""
                SELECT COUNT(*) as missing_customer
                FROM penyewaan p
                LEFT JOIN pelanggan pl ON p.pelanggan_id = pl.id
                WHERE pl.id IS NULL
            """)
            result = cursor.fetchone()
            print(f"3. Penyewaan tanpa pelanggan: {result['missing_customer']}")
            
            # 4. Cek pembayaran tanpa penyewaan
            cursor.execute("""
                SELECT COUNT(*) as orphaned_payments
                FROM pembayaran pb
                LEFT JOIN penyewaan p ON pb.penyewaan_id = p.id
                WHERE p.id IS NULL
            """)
            result = cursor.fetchone()
            print(f"4. Pembayaran tanpa penyewaan: {result['orphaned_payments']}")
            
            # 5. Cek duplikat plat nomor
            cursor.execute("""
                SELECT plat_nomor, COUNT(*) as count
                FROM mobil
                GROUP BY plat_nomor
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            print(f"5. Plat nomor duplikat: {len(duplicates)} ditemukan")
            
            # 6. Cek duplikat NIK
            cursor.execute("""
                SELECT nik, COUNT(*) as count
                FROM pelanggan
                GROUP BY nik
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            print(f"6. NIK duplikat: {len(duplicates)} ditemukan")
            
            return True
            
        except Error as e:
            print(f"❌ Error checking data integrity: {e}")
            return False
        finally:
            cursor.close()
    
    def check_sample_queries(self):
        """Menjalankan query contoh untuk mengecek fungsionalitas"""
        cursor = self.connection.cursor(dictionary=True)
        
        print("\n" + "="*80)
        print("QUERY CONTOH DAN FUNGSIONALITAS")
        print("="*80)
        
        try:
            # Query 1: Mobil tersedia
            print("\n1. 🚗 5 MOBIL TERSEDIA:")
            cursor.execute("""
                SELECT merk, model, tahun, plat_nomor, harga_sewa_per_hari
                FROM mobil 
                WHERE status = 'tersedia'
                ORDER BY harga_sewa_per_hari
                LIMIT 5
            """)
            
            available_cars = cursor.fetchall()
            if available_cars:
                car_data = []
                for car in available_cars:
                    car_data.append([
                        car['merk'],
                        car['model'],
                        car['tahun'],
                        car['plat_nomor'],
                        f"Rp {car['harga_sewa_per_hari']:,.0f}"
                    ])
                
                headers = ["Merk", "Model", "Tahun", "Plat", "Harga/Hari"]
                print(tabulate(car_data, headers=headers, tablefmt="grid"))
            else:
                print("Tidak ada mobil tersedia")
            
            # Query 2: Penyewaan aktif
            print("\n2. 📋 PENYEWAAN AKTIF:")
            cursor.execute("""
                SELECT 
                    p.id,
                    p.tanggal_sewa,
                    p.tanggal_kembali,
                    m.merk,
                    m.model,
                    pl.nama as pelanggan,
                    p.total_biaya
                FROM penyewaan p
                JOIN mobil m ON p.mobil_id = m.id
                JOIN pelanggan pl ON p.pelanggan_id = pl.id
                WHERE p.status = 'aktif'
                ORDER BY p.tanggal_kembali
                LIMIT 5
            """)
            
            active_rentals = cursor.fetchall()
            if active_rentals:
                rental_data = []
                for rental in active_rentals:
                    rental_data.append([
                        rental['id'],
                        rental['tanggal_sewa'],
                        rental['tanggal_kembali'],
                        f"{rental['merk']} {rental['model']}",
                        rental['pelanggan'],
                        f"Rp {rental['total_biaya']:,.0f}"
                    ])
                
                headers = ["ID", "Tanggal Sewa", "Tanggal Kembali", "Mobil", "Pelanggan", "Total"]
                print(tabulate(rental_data, headers=headers, tablefmt="grid"))
            else:
                print("Tidak ada penyewaan aktif")
            
            # Query 3: Statistik
            print("\n3. 📊 STATISTIK SISTEM:")
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM mobil) as total_mobil,
                    (SELECT COUNT(*) FROM mobil WHERE status = 'tersedia') as mobil_tersedia,
                    (SELECT COUNT(*) FROM pelanggan) as total_pelanggan,
                    (SELECT COUNT(*) FROM penyewaan WHERE status = 'aktif') as penyewaan_aktif,
                    (SELECT COUNT(*) FROM penyewaan WHERE status IN ('selesai', 'terlambat')) as penyewaan_selesai,
                    (SELECT COALESCE(SUM(total_biaya + denda), 0) FROM penyewaan) as total_pendapatan
            """)
            
            stats = cursor.fetchone()
            
            stat_data = [
                ["Total Mobil", stats['total_mobil']],
                ["Mobil Tersedia", stats['mobil_tersedia']],
                ["Total Pelanggan", stats['total_pelanggan']],
                ["Penyewaan Aktif", stats['penyewaan_aktif']],
                ["Penyewaan Selesai", stats['penyewaan_selesai']],
                ["Total Pendapatan", f"Rp {stats['total_pendapatan']:,.0f}"]
            ]
            
            print(tabulate(stat_data, tablefmt="grid"))
            
            # Query 4: Pelanggan dengan penyewaan terbanyak
            print("\n4. 🏆 TOP 3 PELANGGAN:")
            cursor.execute("""
                SELECT 
                    pl.nama,
                    pl.nik,
                    COUNT(p.id) as jumlah_penyewaan,
                    COALESCE(SUM(p.total_biaya + p.denda), 0) as total_pengeluaran
                FROM pelanggan pl
                LEFT JOIN penyewaan p ON pl.id = p.pelanggan_id
                GROUP BY pl.id
                ORDER BY jumlah_penyewaan DESC, total_pengeluaran DESC
                LIMIT 3
            """)
            
            top_customers = cursor.fetchall()
            if top_customers:
                customer_data = []
                for customer in top_customers:
                    customer_data.append([
                        customer['nama'],
                        customer['nik'],
                        customer['jumlah_penyewaan'],
                        f"Rp {customer['total_pengeluaran']:,.0f}"
                    ])
                
                headers = ["Nama", "NIK", "Jumlah Sewa", "Total Pengeluaran"]
                print(tabulate(customer_data, headers=headers, tablefmt="grid"))
            
            return True
            
        except Error as e:
            print(f"❌ Error running sample queries: {e}")
            return False
        finally:
            cursor.close()
    
    def check_triggers_and_procedures(self):
        """Mengecek trigger dan stored procedures"""
        cursor = self.connection.cursor(dictionary=True)
        
        print("\n" + "="*80)
        print("TRIGGER DAN STORED PROCEDURES")
        print("="*80)
        
        try:
            # Cek triggers
            cursor.execute("""
                SELECT 
                    TRIGGER_NAME,
                    EVENT_MANIPULATION,
                    EVENT_OBJECT_TABLE,
                    ACTION_TIMING
                FROM INFORMATION_SCHEMA.TRIGGERS
                WHERE TRIGGER_SCHEMA = %s
                ORDER BY EVENT_OBJECT_TABLE, ACTION_TIMING
            """, (self.database,))
            
            triggers = cursor.fetchall()
            
            if triggers:
                print("\n🔧 TRIGGERS:")
                trigger_data = []
                for trigger in triggers:
                    trigger_data.append([
                        trigger['TRIGGER_NAME'],
                        trigger['EVENT_OBJECT_TABLE'],
                        trigger['EVENT_MANIPULATION'],
                        trigger['ACTION_TIMING']
                    ])
                
                headers = ["Nama Trigger", "Tabel", "Event", "Timing"]
                print(tabulate(trigger_data, headers=headers, tablefmt="grid"))
            else:
                print("\n⚠ Tidak ada trigger yang ditemukan")
            
            # Cek stored procedures
            cursor.execute("""
                SELECT 
                    ROUTINE_NAME,
                    ROUTINE_TYPE,
                    CREATED
                FROM INFORMATION_SCHEMA.ROUTINES
                WHERE ROUTINE_SCHEMA = %s
                AND ROUTINE_TYPE = 'PROCEDURE'
                ORDER BY ROUTINE_NAME
            """, (self.database,))
            
            procedures = cursor.fetchall()
            
            if procedures:
                print("\n⚙️ STORED PROCEDURES:")
                proc_data = []
                for proc in procedures:
                    proc_data.append([
                        proc['ROUTINE_NAME'],
                        proc['ROUTINE_TYPE'],
                        proc['CREATED']
                    ])
                
                headers = ["Nama Procedure", "Type", "Dibuat"]
                print(tabulate(proc_data, headers=headers, tablefmt="grid"))
            else:
                print("\n⚠ Tidak ada stored procedure yang ditemukan")
            
            return True
            
        except Error as e:
            print(f"❌ Error checking triggers/procedures: {e}")
            return False
        finally:
            cursor.close()
    
    def run_all_checks(self):
        """Menjalankan semua pengecekan"""
        print("\n" + "="*80)
        print("🔍 SYSTEM CHECK - RENTAL MOBIL DATABASE")
        print("="*80)
        
        # Cek koneksi
        if not self.connect():
            return False
        
        try:
            # 1. Cek tabel
            print("\n📁 STEP 1: CEK TABEL")
            print("-" * 40)
            if not self.check_tables():
                return False
            
            # 2. Cek struktur tabel
            print("\n🔧 STEP 2: CEK STRUKTUR TABEL")
            self.check_table_structure()
            
            # 3. Cek integritas data
            print("\n✅ STEP 3: CEK INTEGRITAS DATA")
            self.check_data_integrity()
            
            # 4. Cek trigger dan procedures
            print("\n⚙️ STEP 4: CEK TRIGGER & PROCEDURES")
            self.check_triggers_and_procedures()
            
            # 5. Jalankan query contoh
            print("\n🚀 STEP 5: TEST QUERY CONTOH")
            self.check_sample_queries()
            
            # Summary
            print("\n" + "="*80)
            print("🎉 CHECK COMPLETE - DATABASE READY FOR USE")
            print("="*80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during system check: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("\n🔌 Koneksi database ditutup")

def main():
    """Fungsi utama"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check Rental Mobil Database')
    parser.add_argument('--host', default='localhost', help='MySQL host')
    parser.add_argument('--user', default='root', help='MySQL username')
    parser.add_argument('--password', default='', help='MySQL password')
    parser.add_argument('--database', default='rental_mobil_db', help='Database name')
    
    args = parser.parse_args()
    
    checker = DatabaseChecker(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    checker.run_all_checks()

if __name__ == "__main__":
    main()