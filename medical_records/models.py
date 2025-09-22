from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment


class MedicalRecord(models.Model):
    """
    Main medical record for patient visits
    """
    RECORD_TYPES = [
        ('consultation', 'Consultation'),
        ('diagnosis', 'Diagnosis'),
        ('treatment', 'Treatment'),
        ('surgery', 'Surgery'),
        ('lab_test', 'Lab Test'),
        ('imaging', 'Imaging'),
        ('vaccination', 'Vaccination'),
        ('emergency', 'Emergency Visit'),
    ]
    
    record_id = models.CharField(max_length=20, unique=True, help_text="Unique medical record identifier")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_records_created')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_records')
    
    # Record details
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, default='consultation')
    visit_date = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True, null=True)  # Alias for created_at
    chief_complaint = models.TextField(help_text="Primary reason for visit")
    history_of_present_illness = models.TextField(blank=True)
    
    # Physical examination
    vital_signs_data = models.JSONField(default=dict, blank=True, help_text="Store vital signs as JSON")
    physical_examination = models.TextField(blank=True)
    
    # Assessment and plan
    assessment = models.TextField(blank=True, help_text="Doctor's assessment")
    diagnosis = models.TextField(blank=True, help_text="Primary and secondary diagnoses")
    treatment_plan = models.TextField(blank=True)
    
    # Follow-up
    follow_up_instructions = models.TextField(blank=True)
    next_visit_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_medical_records')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_private = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-visit_date']
    
    def __str__(self):
        return f"{self.record_id} - {self.patient.user.get_full_name()} ({self.visit_date.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        if not self.record_id:
            # Generate unique record ID
            from django.utils.crypto import get_random_string
            from django.utils import timezone
            self.record_id = f"MR{timezone.now().year}{get_random_string(8, allowed_chars='0123456789').upper()}"
        super().save(*args, **kwargs)


class Prescription(models.Model):
    """
    Prescription model for medications
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('completed', 'Completed'),
        ('discontinued', 'Discontinued'),
        ('cancelled', 'Cancelled'),
    ]
    
    prescription_id = models.CharField(max_length=20, unique=True)
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    prescribed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescribed_medications')
    
    # Prescription details
    date_prescribed = models.DateTimeField(auto_now_add=True, null=True)
    prescribed_date = models.DateTimeField(auto_now_add=True, null=True)  # Alias
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, default="As prescribed")
    frequency = models.CharField(max_length=50, default="As prescribed")
    duration = models.CharField(max_length=100, default="As prescribed")
    refills_remaining = models.PositiveIntegerField(default=0)
    refill_requested = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, help_text="General prescription notes")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        ordering = ['-prescribed_date']
    
    def __str__(self):
        return f"{self.prescription_id} - {self.medication_name} for {self.patient.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.prescription_id:
            # Generate unique prescription ID
            from django.utils.crypto import get_random_string
            from django.utils import timezone
            self.prescription_id = f"RX{timezone.now().year}{get_random_string(8, allowed_chars='0123456789').upper()}"
        super().save(*args, **kwargs)
        if not self.prescription_id:
            # Generate unique prescription ID
            from django.utils.crypto import get_random_string
            from django.utils import timezone
            self.prescription_id = f"RX{timezone.now().year}{get_random_string(8, allowed_chars='0123456789').upper()}"
        super().save(*args, **kwargs)


class PrescriptionMedication(models.Model):
    """
    Individual medications in a prescription
    """
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_times_daily', 'Three Times Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('as_needed', 'As Needed'),
        ('before_meals', 'Before Meals'),
        ('after_meals', 'After Meals'),
        ('at_bedtime', 'At Bedtime'),
        ('every_other_day', 'Every Other Day'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    ROUTE_CHOICES = [
        ('oral', 'Oral'),
        ('topical', 'Topical'),
        ('injection', 'Injection'),
        ('inhaled', 'Inhaled'),
        ('sublingual', 'Sublingual'),
        ('rectal', 'Rectal'),
        ('eye_drops', 'Eye Drops'),
        ('ear_drops', 'Ear Drops'),
    ]
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medications')
    medication_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    strength = models.CharField(max_length=50, help_text="e.g., 500mg, 5ml")
    dosage = models.CharField(max_length=100, default="As prescribed", help_text="e.g., 1 tablet, 2 capsules")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    route = models.CharField(max_length=20, choices=ROUTE_CHOICES, default='oral')
    duration = models.CharField(max_length=100, default="As prescribed", help_text="e.g., 7 days, 2 weeks")
    quantity = models.PositiveIntegerField(help_text="Total quantity to dispense")
    refills = models.PositiveIntegerField(default=0, help_text="Number of refills allowed")
    
    # Instructions
    instructions = models.TextField(blank=True, help_text="Special instructions")
    side_effects = models.TextField(blank=True, help_text="Possible side effects")
    
    # Status
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.medication_name} - {self.strength}"


class LabTest(models.Model):
    """
    Laboratory tests and results
    """
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal'),
    ]
    
    PRIORITY_CHOICES = [
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT'),
    ]
    
    test_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='ordered_lab_tests', null=True, blank=True)
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ordered_lab_tests', null=True, blank=True)
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_tests')
    
    # Test details
    test_name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=100, blank=True)  # For filtering
    test_category = models.CharField(max_length=100, blank=True)
    test_code = models.CharField(max_length=20, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='routine')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    
    # Dates
    ordered_date = models.DateTimeField(auto_now_add=True, null=True)
    date_taken = models.DateTimeField(null=True, blank=True)  # Alias for sample_collected_date
    sample_collected_date = models.DateTimeField(null=True, blank=True)
    result_date = models.DateTimeField(null=True, blank=True)
    
    # Results
    result_value = models.TextField(blank=True)
    reference_range = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    is_abnormal = models.BooleanField(default=False)
    
    # Additional info
    notes = models.TextField(blank=True)
    interpretation = models.TextField(blank=True)
    
    # Files
    result_file = models.FileField(upload_to='uploads/lab_results/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        ordering = ['-ordered_date']
    
    def __str__(self):
        return f"{self.test_id} - {self.test_name} for {self.patient.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.test_id:
            # Generate unique test ID
            from django.utils.crypto import get_random_string
            from django.utils import timezone
            self.test_id = f"LAB{timezone.now().year}{get_random_string(8, allowed_chars='0123456789').upper()}"
        if not self.date_taken and self.sample_collected_date:
            self.date_taken = self.sample_collected_date
        super().save(*args, **kwargs)


# Create an alias for LabResult
LabResult = LabTest


class VitalSigns(models.Model):
    """
    Vital signs measurements
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name='vital_signs')
    measured_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recorded_vitals', null=True, blank=True)  # Alias
    
    # Vital signs
    temperature = models.FloatField(null=True, blank=True, help_text="Temperature in Celsius")
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Beats per minute")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Breaths per minute")
    oxygen_saturation = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="SpO2 percentage"
    )
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    
    # Additional measurements
    pain_scale = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Pain scale 0-10"
    )
    
    # Metadata
    measured_at = models.DateTimeField()
    date_recorded = models.DateTimeField(auto_now_add=True, null=True)  # Alias
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        ordering = ['-measured_at']
        verbose_name_plural = "Vital Signs"
    
    def __str__(self):
        return f"Vital Signs for {self.patient.user.get_full_name()} on {self.measured_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def blood_pressure(self):
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None
    
    @property
    def bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 1)
        return None


# Create alias for VitalSign (singular)
VitalSign = VitalSigns


class Allergy(models.Model):
    """
    Patient allergies
    """
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('life_threatening', 'Life Threatening'),
    ]
    
    ALLERGY_TYPES = [
        ('drug', 'Drug/Medication'),
        ('food', 'Food'),
        ('environmental', 'Environmental'),
        ('contact', 'Contact'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=200, help_text="Name of the allergen")
    allergy_type = models.CharField(max_length=20, choices=ALLERGY_TYPES, default='other')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='mild')
    reaction = models.TextField(help_text="Description of allergic reaction")
    
    # Additional details
    onset_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        ordering = ['-severity', 'allergen']
        verbose_name_plural = "Allergies"
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.allergen} ({self.severity})"
