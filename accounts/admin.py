from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'get_full_name', 'user_type', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_verified', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'date_of_birth', 'address', 'avatar', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'emergency_contact_name', 'preferred_language', 'receive_notifications']
    list_filter = ['preferred_language', 'receive_notifications', 'receive_email_reminders']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'emergency_contact_name']
    
    fieldsets = [
        ('User', {
            'fields': ['user']
        }),
        ('Emergency Contact', {
            'fields': ['emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship']
        }),
        ('Medical Information', {
            'fields': ['medical_alerts']
        }),
        ('Preferences', {
            'fields': ['preferred_language', 'timezone']
        }),
        ('Notifications', {
            'fields': ['receive_notifications', 'receive_email_reminders', 'receive_sms_reminders']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']
