from django.contrib import admin
from django.utils.html import format_html
from .models import Specialization, Doctor, DoctorEducation, DoctorExperience, DoctorAvailability


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'doctor_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def doctor_count(self, obj):
        return obj.doctors.count()
    doctor_count.short_description = 'Number of Doctors'


class DoctorEducationInline(admin.TabularInline):
    model = DoctorEducation
    extra = 1
    fields = ['degree', 'institution', 'year_of_completion', 'grade_or_percentage']


class DoctorExperienceInline(admin.TabularInline):
    model = DoctorExperience
    extra = 1
    fields = ['position', 'hospital_or_clinic', 'start_date', 'end_date', 'responsibilities']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['doctor_id', 'user_full_name', 'qualification', 'years_of_experience', 'rating_display', 'is_verified', 'is_available_for_appointments']
    list_filter = ['qualification', 'is_verified', 'is_available_for_appointments', 'specializations', 'joined_date']
    search_fields = ['doctor_id', 'user__first_name', 'user__last_name', 'user__email', 'medical_license_number']
    ordering = ['-joined_date']
    readonly_fields = ['doctor_id', 'rating', 'total_ratings', 'joined_date', 'created_at', 'updated_at']
    filter_horizontal = ['specializations']
    inlines = [DoctorEducationInline, DoctorExperienceInline]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['user', 'doctor_id', 'medical_license_number', 'qualification', 'years_of_experience']
        }),
        ('Specializations', {
            'fields': ['specializations']
        }),
        ('Professional Details', {
            'fields': ['hospital_affiliation', 'clinic_address', 'consultation_fee', 'bio']
        }),
        ('Schedule & Availability', {
            'fields': ['available_days', 'start_time', 'end_time', 'consultation_duration']
        }),
        ('Status & Verification', {
            'fields': ['is_verified', 'is_available_for_appointments']
        }),
        ('Rating', {
            'fields': ['rating', 'total_ratings'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['joined_date', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def user_full_name(self, obj):
        return f"Dr. {obj.user.get_full_name()}"
    user_full_name.short_description = 'Full Name'
    user_full_name.admin_order_field = 'user__first_name'
    
    def rating_display(self, obj):
        if obj.total_ratings > 0:
            stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
            return format_html(
                '<span title="{} out of 5 stars ({} reviews)">{} ({:.1f})</span>',
                obj.rating, obj.total_ratings, stars, obj.rating
            )
        return "No ratings yet"
    rating_display.short_description = 'Rating'


@admin.register(DoctorEducation)
class DoctorEducationAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'degree', 'institution', 'year_of_completion', 'grade_or_percentage']
    list_filter = ['degree', 'year_of_completion']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'degree', 'institution']
    ordering = ['-year_of_completion']


@admin.register(DoctorExperience)
class DoctorExperienceAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'position', 'hospital_or_clinic', 'start_date', 'end_date', 'is_current']
    list_filter = ['start_date', 'end_date']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'position', 'hospital_or_clinic']
    ordering = ['-start_date']


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'availability_type', 'start_time', 'end_time', 'reason']
    list_filter = ['availability_type', 'date']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'reason']
    ordering = ['date', 'start_time']
