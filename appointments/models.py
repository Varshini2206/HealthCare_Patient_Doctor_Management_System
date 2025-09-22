from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import Patient
from doctors.models import Doctor


class Appointment(models.Model):
    """
    Appointment booking model
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    APPOINTMENT_TYPES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('check_up', 'Check-up'),
        ('emergency', 'Emergency'),
        ('procedure', 'Procedure'),
        ('surgery', 'Surgery'),
        ('therapy', 'Therapy'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    appointment_id = models.CharField(max_length=20, unique=True, help_text="Unique appointment identifier")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    
    # Appointment details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES, default='consultation')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Details
    chief_complaint = models.TextField(help_text="Main reason for visit")
    symptoms = models.TextField(blank=True, help_text="Current symptoms")
    notes = models.TextField(blank=True, help_text="Additional notes from patient")
    doctor_notes = models.TextField(blank=True, help_text="Doctor's notes during appointment")
    
    # Billing
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_instructions = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='cancelled_appointments'
    )
    cancellation_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
    
    def __str__(self):
        return f"{self.appointment_id} - {self.patient.user.get_full_name()} with Dr. {self.doctor.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.appointment_id:
            # Generate unique appointment ID
            from django.utils.crypto import get_random_string
            self.appointment_id = f"A{timezone.now().year}{get_random_string(8, allowed_chars='0123456789').upper()}"
        
        # Set consultation fee from doctor if not set
        if not self.consultation_fee and self.doctor.consultation_fee:
            self.consultation_fee = self.doctor.consultation_fee
            
        super().save(*args, **kwargs)
    
    @property
    def appointment_datetime(self):
        return timezone.datetime.combine(self.appointment_date, self.appointment_time)
    
    @property
    def is_upcoming(self):
        return self.appointment_datetime > timezone.now() and self.status in ['scheduled', 'confirmed']
    
    @property
    def is_past(self):
        return self.appointment_datetime < timezone.now()
    
    @property
    def can_be_cancelled(self):
        return self.status in ['scheduled', 'confirmed'] and self.appointment_datetime > timezone.now()
    
    def cancel_appointment(self, cancelled_by, reason=""):
        """Cancel the appointment"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason
        self.save()
    
    def reschedule_appointment(self, new_date, new_time, updated_by):
        """Reschedule the appointment"""
        # Create a record of the original appointment
        AppointmentHistory.objects.create(
            appointment=self,
            action='rescheduled',
            old_date=self.appointment_date,
            old_time=self.appointment_time,
            new_date=new_date,
            new_time=new_time,
            action_by=updated_by,
        )
        
        self.appointment_date = new_date
        self.appointment_time = new_time
        self.status = 'rescheduled'
        self.save()


class AppointmentHistory(models.Model):
    """
    Track appointment changes and history
    """
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('confirmed', 'Confirmed'),
        ('rescheduled', 'Rescheduled'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    old_date = models.DateField(null=True, blank=True)
    old_time = models.TimeField(null=True, blank=True)
    new_date = models.DateField(null=True, blank=True)
    new_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    action_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-action_at']
    
    def __str__(self):
        return f"{self.appointment.appointment_id} - {self.action} at {self.action_at}"


class AppointmentRating(models.Model):
    """
    Patient rating and feedback for appointments
    """
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='rating')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    review = models.TextField(blank=True, help_text="Patient review")
    would_recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.appointment.appointment_id} - {self.rating} stars"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update doctor's overall rating
        self.appointment.doctor.update_rating(self.rating)


class AppointmentReminder(models.Model):
    """
    Reminder notifications for appointments
    """
    REMINDER_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPES)
    reminder_time = models.DateTimeField()
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['reminder_time']
    
    def __str__(self):
        return f"{self.appointment.appointment_id} - {self.reminder_type} reminder"
