#!/usr/bin/env python
"""
Script untuk menjalankan setup database dengan input otomatis
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_database import DatabaseCreator

def main():
    """Run setup dengan konfigurasi default"""
    db_creator = DatabaseCreator(host='localhost', user='root', password=None)
    
    try:
        # Connect to MySQL
        if not db_creator.connect_without_db():
            print("Gagal terhubung ke MySQL server")
            sys.exit(1)
        
        # Create database (with automatic drop)
        cursor = db_creator.connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {db_creator.database_name}")
        db_creator.print_warning(f"Database '{db_creator.database_name}' dihapus (jika ada)")
        
        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS {db_creator.database_name} 
            CHARACTER SET utf8mb4 
            COLLATE utf8mb4_unicode_ci
        """)
        cursor.execute(f"USE {db_creator.database_name}")
        cursor.close()
        db_creator.print_success(f"Database '{db_creator.database_name}' berhasil dibuat")
        
        # Create tables
        if not db_creator.create_tables():
            print("Gagal membuat tabel")
            sys.exit(1)
        
        # Create indexes
        if not db_creator.create_indexes():
            print("Gagal membuat indexes")
            sys.exit(1)
        
        # Create triggers
        if not db_creator.create_triggers():
            print("Gagal membuat triggers")
            sys.exit(1)
        
        # Create views
        if not db_creator.create_views():
            print("Gagal membuat views")
            sys.exit(1)
        
        # Create stored procedures
        if not db_creator.create_stored_procedures():
            print("Gagal membuat stored procedures")
            sys.exit(1)
        
        # Insert sample data
        db_creator.insert_sample_data()
        
        # Close connection
        if db_creator.connection:
            db_creator.connection.close()
        
        # Reconnect with database
        if not db_creator.connect_with_db():
            print("Gagal terhubung ke database")
            sys.exit(1)
        
        # Show summary
        db_creator.show_database_summary()
        
        print(f"\n{db_creator.COLORS['OKGREEN']}{'='*60}{db_creator.COLORS['ENDC']}")
        print(f"{db_creator.COLORS['OKGREEN']}✓ SETUP DATABASE BERHASIL!{db_creator.COLORS['ENDC']}")
        print(f"{db_creator.COLORS['OKGREEN']}{'='*60}{db_creator.COLORS['ENDC']}")
        
    except KeyboardInterrupt:
        print(f"\n\n{chr(0x1F6AB)} Setup dibatalkan oleh user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{chr(0x1F6AB)} Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
