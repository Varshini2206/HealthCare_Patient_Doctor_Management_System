import logging
import json
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

# Configure audit logger
audit_logger = logging.getLogger('audit')

class AuditMiddleware:
    """
    Middleware for logging sensitive healthcare data access
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Sensitive paths that require audit logging
        self.sensitive_paths = [
            '/patients/',
            '/medical-records/',
            '/api/v1/patients/',
            '/api/v1/medical-records/',
        ]
        
        # Exclude paths from audit logging
        self.exclude_paths = [
            '/static/',
            '/media/',
            '/admin/jsi18n/',
        ]

    def __call__(self, request):
        # Process request
        start_time = timezone.now()
        
        # Get response
        response = self.get_response(request)
        
        # Log sensitive operations
        if self.should_audit(request):
            self.log_access(request, response, start_time)
        
        return response

    def should_audit(self, request):
        """
        Determine if request should be audited
        """
        path = request.path
        
        # Skip excluded paths
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return False
        
        # Check if path is sensitive
        for sensitive_path in self.sensitive_paths:
            if path.startswith(sensitive_path):
                return True
        
        # Audit all POST, PUT, DELETE operations on healthcare data
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            healthcare_paths = ['/patients/', '/doctors/', '/appointments/', '/medical-records/']
            for hc_path in healthcare_paths:
                if path.startswith(hc_path):
                    return True
        
        return False

    def log_access(self, request, response, start_time):
        """
        Log the access attempt
        """
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        # Prepare audit log entry
        audit_entry = {
            'timestamp': start_time.isoformat(),
            'user': self.get_user_info(request.user),
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'response_status': response.status_code,
            'duration_seconds': duration,
            'session_key': request.session.session_key,
        }
        
        # Add request body for POST/PUT operations (excluding sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH']:
            audit_entry['has_request_body'] = len(request.body) > 0
            audit_entry['content_type'] = request.content_type
        
        # Log the entry
        audit_logger.info(json.dumps(audit_entry))

    def get_user_info(self, user):
        """
        Get user information for audit log
        """
        if isinstance(user, AnonymousUser):
            return {'id': None, 'username': 'anonymous', 'type': 'anonymous'}
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'type': getattr(user, 'user_type', 'unknown'),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }

    def get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers for healthcare data protection
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Add HSTS header for HTTPS
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response