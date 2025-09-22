from django.contrib import admin
from django.utils.html import format_html
from .models import Patient, PatientDocument


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'user_full_name', 'user_email', 'age', 'gender', 'blood_group', 'is_active', 'registration_date']
    list_filter = ['gender', 'blood_group', 'marital_status', 'is_active', 'registration_date']
    search_fields = ['patient_id', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['-registration_date']
    readonly_fields = ['patient_id', 'age', 'bmi', 'registration_date', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['user', 'patient_id', 'gender', 'blood_group']
        }),
        ('Physical Information', {
            'fields': ['height', 'weight', 'bmi']
        }),
        ('Personal Information', {
            'fields': ['marital_status', 'occupation']
        }),
        ('Insurance Information', {
            'fields': ['insurance_provider', 'insurance_policy_number']
        }),
        ('Medical Information', {
            'fields': ['known_allergies', 'chronic_conditions', 'current_medications', 'family_medical_history']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
        ('Timestamps', {
            'fields': ['registration_date', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Full Name'
    user_full_name.admin_order_field = 'user__first_name'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'


@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'document_type', 'upload_date', 'uploaded_by', 'file_size_display']
    list_filter = ['document_type', 'is_private', 'upload_date']
    search_fields = ['title', 'patient__patient_id', 'patient__user__first_name', 'patient__user__last_name']
    ordering = ['-upload_date']
    readonly_fields = ['upload_date', 'file_size_display', 'file_extension']
    
    fieldsets = [
        ('Document Information', {
            'fields': ['title', 'document_type', 'file', 'description']
        }),
        ('Patient Information', {
            'fields': ['patient']
        }),
        ('Upload Information', {
            'fields': ['uploaded_by', 'upload_date', 'is_private']
        }),
        ('File Information', {
            'fields': ['file_size_display', 'file_extension'],
            'classes': ['collapse']
        }),
    ]
    
    def file_size_display(self, obj):
        size = obj.file_size
        if size:
            if size > 1024 * 1024:
                return f"{size / (1024 * 1024):.1f} MB"
            elif size > 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size} bytes"
        return "N/A"
    file_size_display.short_description = 'File Size'
    
    def file_extension(self, obj):
        return obj.get_file_extension()
    file_extension.short_description = 'File Type'
