"""
Middleware untuk logging request dan aktivitas
"""
import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('rental')
security_logger = logging.getLogger('django.security')


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
