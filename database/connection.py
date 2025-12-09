import mysql.connector
from mysql.connector import Error, pooling
from config import Config

class DatabaseConnectionPool:
    """Menggunakan Connection Pool untuk efisiensi koneksi (Singleton Pattern)"""
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_pool()
        return cls._instance
    
    @classmethod
    def _initialize_pool(cls):
        """Inisialisasi connection pool"""
        try:
            db_config = Config.get_db_config()
            cls._connection_pool = pooling.MySQLConnectionPool(
                pool_name="rental_pool",
                pool_size=5,
                **db_config
            )
            print("Connection pool created successfully")
        except Error as e:
            print(f"Error creating connection pool: {e}")
            raise
    
    def get_connection(self):
        """Mendapatkan koneksi dari pool"""
        if self._connection_pool:
            return self._connection_pool.get_connection()
        raise Exception("Connection pool not initialized")
    
    @classmethod
    def close_all_connections(cls):
        """Menutup semua koneksi dalam pool"""
        if cls._connection_pool:
            cls._connection_pool._remove_connections()


class DatabaseManager:
    """Manager untuk database operations dengan connection pooling"""
    
    def __init__(self):
        self.pool = DatabaseConnectionPool()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute query dengan optional fetch result"""
        connection = None
        cursor = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                # Return last insert id untuk INSERT queries
                if 'INSERT' in query.upper():
                    connection.commit()
                    return cursor.lastrowid
                else:
                    result = cursor.fetchall()
                    return result
            else:
                connection.commit()
                return cursor.rowcount
                
        except Error as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_query_one(self, query: str, params: tuple = None):
        """Execute query dan return satu row"""
        connection = None
        cursor = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            return result
                
        except Error as e:
            raise e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_query_many(self, query: str, params: tuple = None):
        """Execute query dan return semua rows"""
        connection = None
        cursor = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchall()
            return result
                
        except Error as e:
            raise e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_call_procedure(self, procedure_name: str, args: list = None):
        """Execute stored procedure"""
        connection = None
        cursor = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            
            cursor.callproc(procedure_name, args or [])
            connection.commit()
            
            # Get result dari procedure
            results = []
            for result in cursor.stored_results():
                results.append(result.fetchall())
            
            return results
                
        except Error as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()