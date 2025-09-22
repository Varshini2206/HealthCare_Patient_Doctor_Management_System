from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import date


class Patient(models.Model):
    """
    Patient model extending the basic user information
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('Unknown', 'Unknown'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    patient_id = models.CharField(max_length=20, unique=True, help_text="Unique patient identifier")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='Unknown')
    height = models.FloatField(null=True, blank=True, help_text="Height in centimeters")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kilograms")
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)
    
    # Medical Information
    known_allergies = models.TextField(blank=True, help_text="Known allergies")
    chronic_conditions = models.TextField(blank=True, help_text="Ongoing medical conditions")
    current_medications = models.TextField(blank=True, help_text="Current medications")
    family_medical_history = models.TextField(blank=True, help_text="Family medical history")
    
    # Registration details
    registration_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-registration_date']
        
    def __str__(self):
        return f"{self.patient_id} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            # Generate unique patient ID
            from django.utils.crypto import get_random_string
            self.patient_id = f"P{timezone.now().year}{get_random_string(6, allowed_chars='0123456789').upper()}"
        super().save(*args, **kwargs)
    
    @property
    def age(self):
        if self.user.date_of_birth:
            today = date.today()
            return today.year - self.user.date_of_birth.year - (
                (today.month, today.day) < (self.user.date_of_birth.month, self.user.date_of_birth.day)
            )
        return None
    
    @property
    def bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 1)
        return None
    
    def get_bmi_category(self):
        bmi = self.bmi
        if bmi is None:
            return "Unknown"
        elif bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obesity"


class PatientDocument(models.Model):
    """
    Model for storing patient documents and test results
    """
    DOCUMENT_TYPES = [
        ('medical_report', 'Medical Report'),
        ('lab_result', 'Lab Result'),
        ('xray', 'X-Ray'),
        ('prescription', 'Prescription'),
        ('insurance', 'Insurance Document'),
        ('id_proof', 'ID Proof'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other')
    file = models.FileField(upload_to='uploads/documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False, help_text="Private documents visible only to patient and assigned doctors")
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.title} - {self.patient.patient_id}"
    
    @property
    def file_size(self):
        if self.file:
            return self.file.size
        return 0
    
    def get_file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return ""
