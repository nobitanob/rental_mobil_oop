import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Konfigurasi database menggunakan prinsip Single Responsibility"""
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'rental_mobil_db')
    
    @classmethod
    def get_db_config(cls):
        """Factory method untuk mendapatkan konfigurasi database"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME
        }