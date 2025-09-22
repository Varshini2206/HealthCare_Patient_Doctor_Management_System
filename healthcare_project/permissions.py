from rest_framework import permissions
from django.core.exceptions import PermissionDenied


class IsOwnerOrHealthcareProvider(permissions.BasePermission):
    """
    Permission to allow access to owners or healthcare providers
    """
    def has_object_permission(self, request, view, obj):
        # Allow read permissions to any authenticated user for safe methods
        if request.method in permissions.SAFE_METHODS:
            # Patients can only see their own data
            if request.user.user_type == 'patient':
                return hasattr(obj, 'user') and obj.user == request.user
            # Healthcare providers can see all patient data
            elif request.user.user_type in ['doctor', 'admin', 'staff']:
                return True
        
        # Write permissions for object owner or healthcare providers
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.user_type in ['doctor', 'admin', 'staff']
        
        return request.user.user_type in ['admin', 'staff']


class IsPatient(permissions.BasePermission):
    """
    Permission to allow access to patients only
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'patient'


class IsDoctor(permissions.BasePermission):
    """
    Permission to allow access to doctors only
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'doctor'


class IsHealthcareProvider(permissions.BasePermission):
    """
    Permission to allow access to healthcare providers (doctors, admin, staff)
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.user_type in ['doctor', 'admin', 'staff'])


class IsAdminOrStaff(permissions.BasePermission):
    """
    Permission to allow access to admin or staff only
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.user_type in ['admin', 'staff'])


class CanViewMedicalRecords(permissions.BasePermission):
    """
    Permission for viewing medical records with specific rules
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Doctors and healthcare staff can view medical records
        if request.user.user_type in ['doctor', 'admin', 'staff']:
            return True
        
        # Patients can only view their own records
        if request.user.user_type == 'patient':
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Healthcare providers can access any medical record
        if request.user.user_type in ['doctor', 'admin', 'staff']:
            return True
        
        # Patients can only access their own medical records
        if request.user.user_type == 'patient' and hasattr(obj, 'patient'):
            from patients.models import Patient
            try:
                patient = Patient.objects.get(user=request.user)
                return obj.patient == patient
            except Patient.DoesNotExist:
                return False
        
        return False


class CanManageAppointments(permissions.BasePermission):
    """
    Permission for managing appointments
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # All authenticated users can view appointments (with filtering)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Patients can create appointments for themselves
        if request.method == 'POST' and request.user.user_type == 'patient':
            return True
        
        # Healthcare providers can manage all appointments
        if request.user.user_type in ['doctor', 'admin', 'staff']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Healthcare providers can manage any appointment
        if request.user.user_type in ['admin', 'staff']:
            return True
        
        # Doctors can manage their own appointments
        if request.user.user_type == 'doctor':
            from doctors.models import Doctor
            try:
                doctor = Doctor.objects.get(user=request.user)
                return obj.doctor == doctor
            except Doctor.DoesNotExist:
                return False
        
        # Patients can manage their own appointments
        if request.user.user_type == 'patient':
            from patients.models import Patient
            try:
                patient = Patient.objects.get(user=request.user)
                return obj.patient == patient
            except Patient.DoesNotExist:
                return False
        
        return False


def check_healthcare_access(user, obj, action='view'):
    """
    Helper function to check healthcare data access permissions
    """
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required")
    
    # Admin and staff have full access
    if user.user_type in ['admin', 'staff']:
        return True
    
    # Doctors have access to patient data for medical purposes
    if user.user_type == 'doctor' and action in ['view', 'update']:
        return True
    
    # Patients can only access their own data
    if user.user_type == 'patient':
        if hasattr(obj, 'user') and obj.user == user:
            return True
        if hasattr(obj, 'patient'):
            from patients.models import Patient
            try:
                patient = Patient.objects.get(user=user)
                return obj.patient == patient
            except Patient.DoesNotExist:
                pass
    
    raise PermissionDenied("Insufficient permissions to access this resource")


class RoleBasedPermissionMixin:
    """
    Mixin to add role-based permission checking to views
    """
    def check_permissions(self, request):
        super().check_permissions(request)
        
        # Additional role-based checks
        if hasattr(self, 'required_user_types'):
            if not request.user.is_authenticated:
                self.permission_denied(request)
            
            if request.user.user_type not in self.required_user_types:
                self.permission_denied(request, message="Insufficient role privileges")


# Decorator for view functions
def require_user_types(*user_types):
    """
    Decorator to require specific user types for view access
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")
            
            if request.user.user_type not in user_types:
                raise PermissionDenied(f"Access restricted to: {', '.join(user_types)}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator