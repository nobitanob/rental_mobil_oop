"""
Middleware untuk logging request dan aktivitas
"""
import logging
import time
import json
import threading
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('rental')
security_logger = logging.getLogger('rental.security')

# Thread local storage untuk menyimpan request
_thread_locals = threading.local()


def get_current_request():
    """Dapatkan request saat ini dari thread local"""
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """Dapatkan user yang sedang login"""
    request = get_current_request()
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None


def get_current_username():
    """Dapatkan username yang sedang login"""
    user = get_current_user()
    if user:
        return user.username
    return 'system'


def get_client_ip():
    """Dapatkan IP address dari request"""
    request = get_current_request()
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    return None


def get_user_agent():
    """Dapatkan User Agent dari request"""
    request = get_current_request()
    if request:
        return request.META.get('HTTP_USER_AGENT', '')[:255]
    return ''


class CurrentUserMiddleware:
    """
    Middleware untuk menyimpan request ke thread local storage.
    Memungkinkan akses ke current user dari mana saja (signals, services, dll)
    
    PENTING: Middleware ini harus dipasang SETELAH AuthenticationMiddleware
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Simpan request ke thread local
        _thread_locals.request = request
        
        response = self.get_response(request)
        
        # Bersihkan setelah request selesai
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware untuk logging semua HTTP request"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log request info
        logger.info(
            f"Request: {request.method} {request.path} - "
            f"IP: {self.get_client_ip(request)} - "
            f"User: {request.user if hasattr(request, 'user') else 'Anonymous'}"
        )
    
    def process_response(self, request, response):
        # Hitung waktu proses
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            duration_ms = int(duration * 1000)
        else:
            duration_ms = 0
        
        # Log response info
        log_message = (
            f"Response: {request.method} {request.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration_ms}ms"
        )
        
        if response.status_code >= 500:
            logger.error(log_message)
        elif response.status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        return response
    
    def process_exception(self, request, exception):
        # Log exception
        logger.exception(
            f"Exception pada {request.method} {request.path}: {str(exception)}"
        )
    
    @staticmethod
    def get_client_ip(request):
        """Mendapatkan IP address client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityLoggingMiddleware(MiddlewareMixin):
    """Middleware untuk logging aktivitas keamanan"""
    
    def process_request(self, request):
        # Log suspicious activities
        ip = self.get_client_ip(request)
        
        # Deteksi potential SQL injection
        suspicious_patterns = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', '--', ';']
        query_string = request.META.get('QUERY_STRING', '')
        
        for pattern in suspicious_patterns:
            if pattern.lower() in query_string.lower():
                security_logger.warning(
                    f"Potential SQL Injection attempt dari IP: {ip} - "
                    f"Path: {request.path} - Query: {query_string}"
                )
                break
        
        # Log akses ke admin
        if '/admin/' in request.path:
            security_logger.info(
                f"Admin access: {request.method} {request.path} - "
                f"IP: {ip} - User: {request.user if hasattr(request, 'user') else 'Anonymous'}"
            )
    
    @staticmethod
    def get_client_ip(request):
        """Mendapatkan IP address client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserActivityMiddleware(MiddlewareMixin):
    """Middleware untuk tracking aktivitas user"""
    
    def process_request(self, request):
        # Simpan info request untuk digunakan di signal
        request.client_ip = self.get_client_ip(request)
        request.user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    @staticmethod
    def get_client_ip(request):
        """Mendapatkan IP address client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
