from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Appointment, AppointmentHistory, AppointmentRating, AppointmentReminder


class AppointmentHistoryInline(admin.TabularInline):
    model = AppointmentHistory
    extra = 0
    readonly_fields = ['action', 'old_date', 'old_time', 'new_date', 'new_time', 'action_by', 'action_at']
    can_delete = False


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient_name', 'doctor_name', 'appointment_date', 'appointment_time', 'status', 'priority', 'is_paid']
    list_filter = ['status', 'priority', 'appointment_type', 'appointment_date', 'is_paid', 'created_at']
    search_fields = ['appointment_id', 'patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name', 'doctor__user__last_name']
    ordering = ['appointment_date', 'appointment_time']
    readonly_fields = ['appointment_id', 'appointment_datetime', 'is_upcoming', 'is_past', 'can_be_cancelled', 'created_at', 'updated_at']
    date_hierarchy = 'appointment_date'
    inlines = [AppointmentHistoryInline]
    
    fieldsets = [
        ('Appointment Details', {
            'fields': ['appointment_id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'duration']
        }),
        ('Appointment Information', {
            'fields': ['appointment_type', 'priority', 'status']
        }),
        ('Medical Details', {
            'fields': ['chief_complaint', 'symptoms', 'notes', 'doctor_notes']
        }),
        ('Billing', {
            'fields': ['consultation_fee', 'is_paid', 'payment_method']
        }),
        ('Follow-up', {
            'fields': ['follow_up_required', 'follow_up_date', 'follow_up_instructions']
        }),
        ('Cancellation', {
            'fields': ['cancelled_at', 'cancelled_by', 'cancellation_reason'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_by', 'created_at', 'updated_at', 'appointment_datetime', 'is_upcoming', 'is_past', 'can_be_cancelled'],
            'classes': ['collapse']
        }),
    ]
    
    def patient_name(self, obj):
        return obj.patient.user.get_full_name()
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'patient__user__first_name'
    
    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"
    doctor_name.short_description = 'Doctor'
    doctor_name.admin_order_field = 'doctor__user__first_name'
    
    def get_list_display_status(self, obj):
        status_colors = {
            'scheduled': 'orange',
            'confirmed': 'blue',
            'in_progress': 'purple',
            'completed': 'green',
            'cancelled': 'red',
            'no_show': 'darkred',
            'rescheduled': 'brown',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )
    get_list_display_status.short_description = 'Status'


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'action', 'old_date', 'old_time', 'new_date', 'new_time', 'action_by', 'action_at']
    list_filter = ['action', 'action_at']
    search_fields = ['appointment__appointment_id', 'action_by__first_name', 'action_by__last_name']
    ordering = ['-action_at']
    readonly_fields = ['appointment', 'action', 'old_date', 'old_time', 'new_date', 'new_time', 'action_by', 'action_at']


@admin.register(AppointmentRating)
class AppointmentRatingAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'rating', 'would_recommend', 'created_at']
    list_filter = ['rating', 'would_recommend', 'created_at']
    search_fields = ['appointment__appointment_id', 'appointment__patient__user__first_name', 'appointment__patient__user__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_type', 'reminder_time', 'is_sent', 'sent_at']
    list_filter = ['reminder_type', 'is_sent', 'reminder_time']
    search_fields = ['appointment__appointment_id']
    ordering = ['reminder_time']
    readonly_fields = ['sent_at', 'created_at']
