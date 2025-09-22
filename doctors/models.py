from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Specialization(models.Model):
    """
    Medical specializations for doctors
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Doctor(models.Model):
    """
    Doctor profile model
    """
    QUALIFICATION_LEVELS = [
        ('MBBS', 'MBBS'),
        ('MD', 'MD'),
        ('MS', 'MS'),
        ('DM', 'DM'),
        ('MCh', 'MCh'),
        ('DNB', 'DNB'),
        ('FRCS', 'FRCS'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    doctor_id = models.CharField(max_length=20, unique=True, help_text="Unique doctor identifier")
    medical_license_number = models.CharField(max_length=50, unique=True)
    specializations = models.ManyToManyField(Specialization, related_name='doctors')
    qualification = models.CharField(max_length=20, choices=QUALIFICATION_LEVELS, default='MBBS')
    years_of_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(60)]
    )
    
    # Professional details
    hospital_affiliation = models.CharField(max_length=200, blank=True)
    clinic_address = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bio = models.TextField(blank=True, help_text="Professional biography")
    
    # Schedule and availability
    available_days = models.CharField(
        max_length=50, 
        default='Monday,Tuesday,Wednesday,Thursday,Friday',
        help_text="Comma-separated days (Monday,Tuesday,etc.)"
    )
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='17:00')
    consultation_duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    
    # Status and verification
    is_verified = models.BooleanField(default=False)
    is_available_for_appointments = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Dates
    joined_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-joined_date']
    
    def __str__(self):
        specializations = ", ".join([spec.name for spec in self.specializations.all()[:2]])
        return f"Dr. {self.user.get_full_name()} - {specializations}"
    
    def save(self, *args, **kwargs):
        if not self.doctor_id:
            # Generate unique doctor ID
            from django.utils.crypto import get_random_string
            from django.utils import timezone
            self.doctor_id = f"D{timezone.now().year}{get_random_string(6, allowed_chars='0123456789').upper()}"
        super().save(*args, **kwargs)
    
    @property
    def average_rating(self):
        if self.total_ratings > 0:
            return round(self.rating, 1)
        return 0.0
    
    def get_available_days_list(self):
        return [day.strip() for day in self.available_days.split(',') if day.strip()]
    
    def update_rating(self, new_rating):
        """Update doctor rating with new rating value"""
        total_score = self.rating * self.total_ratings
        self.total_ratings += 1
        self.rating = (total_score + new_rating) / self.total_ratings
        self.save()


class DoctorEducation(models.Model):
    """
    Doctor's educational background
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=200)
    year_of_completion = models.PositiveIntegerField()
    grade_or_percentage = models.CharField(max_length=20, blank=True)
    
    class Meta:
        ordering = ['-year_of_completion']
    
    def __str__(self):
        return f"{self.degree} from {self.institution} ({self.year_of_completion})"


class DoctorExperience(models.Model):
    """
    Doctor's professional experience
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='experience')
    position = models.CharField(max_length=100)
    hospital_or_clinic = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave empty if current position")
    responsibilities = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.hospital_or_clinic}"
    
    @property
    def is_current(self):
        return self.end_date is None


class DoctorAvailability(models.Model):
    """
    Special availability or unavailability periods for doctors
    """
    AVAILABILITY_TYPES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('holiday', 'Holiday'),
        ('conference', 'Conference'),
        ('emergency', 'Emergency'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability_schedule')
    date = models.DateField()
    availability_type = models.CharField(max_length=20, choices=AVAILABILITY_TYPES)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.date} ({self.availability_type})"
