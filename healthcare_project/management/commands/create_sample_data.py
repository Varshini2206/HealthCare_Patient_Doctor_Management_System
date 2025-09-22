from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import CustomUser, UserProfile
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from medical_records.models import MedicalRecord, Prescription, LabTest, VitalSigns
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for healthcare system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--patients',
            type=int,
            default=10,
            help='Number of patients to create'
        )
        parser.add_argument(
            '--doctors',
            type=int,
            default=5,
            help='Number of doctors to create'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample doctors
        doctors = self.create_doctors(options['doctors'])
        
        # Create sample patients
        patients = self.create_patients(options['patients'])
        
        # Create sample appointments
        self.create_appointments(patients, doctors)
        
        # Create sample medical records
        self.create_medical_records(patients, doctors)
        
        # Create sample prescriptions
        self.create_prescriptions(patients, doctors)
        
        # Create sample lab tests
        self.create_lab_tests(patients, doctors)
        
        # Create sample vital signs
        self.create_vital_signs(patients)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data: {len(doctors)} doctors, {len(patients)} patients'
            )
        )

    def create_doctors(self, count):
        doctors = []
        specializations = [
            'Cardiology', 'Dermatology', 'Endocrinology', 'General Medicine',
            'Neurology', 'Orthopedics', 'Pediatrics', 'Psychiatry'
        ]
        
        doctor_names = [
            ('Sarah', 'Johnson'), ('Michael', 'Brown'), ('Emily', 'Wilson'),
            ('David', 'Davis'), ('Jennifer', 'Lee'), ('Robert', 'Miller'),
            ('Lisa', 'Garcia'), ('James', 'Rodriguez')
        ]
        
        for i in range(count):
            first_name, last_name = doctor_names[i % len(doctor_names)]
            email = f"{first_name.lower()}.{last_name.lower()}@healthcenter.com"
            
            # Skip if user already exists
            if User.objects.filter(email=email).exists():
                continue
                
            user = User.objects.create_user(
                username=f"dr_{first_name.lower()}_{last_name.lower()}",
                email=email,
                password="healthpass123",
                first_name=first_name,
                last_name=last_name,
                user_type='doctor',
                phone=f"+1555{random.randint(1000000, 9999999)}"
            )
            
            doctor = Doctor.objects.create(
                user=user,
                license_number=f"LIC{random.randint(100000, 999999)}",
                specialization=specializations[i % len(specializations)],
                qualifications="MD, Board Certified",
                experience_years=random.randint(5, 25),
                consultation_fee=random.randint(150, 400),
                bio=f"Experienced {specializations[i % len(specializations)]} specialist with {random.randint(5, 25)} years of practice.",
                is_available=True
            )
            doctors.append(doctor)
            
        return doctors

    def create_patients(self, count):
        patients = []
        patient_names = [
            ('John', 'Smith'), ('Mary', 'Johnson'), ('Robert', 'Davis'),
            ('Lisa', 'Wilson'), ('William', 'Brown'), ('Patricia', 'Jones'),
            ('James', 'Garcia'), ('Jennifer', 'Martinez'), ('Michael', 'Anderson'),
            ('Linda', 'Taylor'), ('David', 'Thomas'), ('Barbara', 'Hernandez')
        ]
        
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        genders = ['M', 'F']
        
        for i in range(count):
            first_name, last_name = patient_names[i % len(patient_names)]
            email = f"{first_name.lower()}.{last_name.lower()}{i}@email.com"
            
            # Skip if user already exists
            if User.objects.filter(email=email).exists():
                continue
                
            user = User.objects.create_user(
                username=f"patient_{first_name.lower()}_{last_name.lower()}_{i}",
                email=email,
                password="patientpass123",
                first_name=first_name,
                last_name=last_name,
                user_type='patient',
                phone=f"+1555{random.randint(1000000, 9999999)}"
            )
            
            # Random birth date between 20 and 80 years ago
            birth_date = timezone.now().date() - timedelta(days=random.randint(20*365, 80*365))
            
            patient = Patient.objects.create(
                user=user,
                date_of_birth=birth_date,
                gender=random.choice(genders),
                blood_type=random.choice(blood_types),
                address=f"{random.randint(100, 9999)} Main Street, City, State {random.randint(10000, 99999)}",
                emergency_contact_name=f"Emergency Contact {i+1}",
                emergency_contact_phone=f"+1555{random.randint(1000000, 9999999)}",
                insurance_provider=f"Health Insurance {random.randint(1, 5)}",
                insurance_policy_number=f"POL{random.randint(100000, 999999)}"
            )
            patients.append(patient)
            
        return patients

    def create_appointments(self, patients, doctors):
        if not doctors or not patients:
            return
            
        statuses = ['confirmed', 'pending', 'completed', 'cancelled']
        appointment_types = ['routine', 'follow-up', 'consultation', 'emergency']
        
        for i in range(min(20, len(patients) * 2)):  # Create up to 20 appointments
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            
            # Random date between 30 days ago and 30 days from now
            appointment_date = timezone.now().date() + timedelta(days=random.randint(-30, 30))
            appointment_time = timezone.time(hour=random.randint(9, 16), minute=random.choice([0, 30]))
            
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                appointment_type=random.choice(appointment_types),
                reason=f"Medical consultation for {patient.user.first_name}",
                status=random.choice(statuses),
                notes="Sample appointment created for testing"
            )

    def create_medical_records(self, patients, doctors):
        if not doctors or not patients:
            return
            
        record_types = ['consultation', 'diagnosis', 'treatment', 'lab_test']
        
        for i in range(min(15, len(patients))):  # Create medical records
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            
            visit_date = timezone.now() - timedelta(days=random.randint(1, 90))
            
            MedicalRecord.objects.create(
                patient=patient,
                doctor=doctor,
                record_type=random.choice(record_types),
                visit_date=visit_date,
                chief_complaint=f"Patient complaint for {patient.user.first_name}",
                assessment="Medical assessment completed",
                diagnosis="Sample diagnosis",
                treatment_plan="Recommended treatment plan",
                created_by=doctor.user
            )

    def create_prescriptions(self, patients, doctors):
        if not doctors or not patients:
            return
            
        medications = [
            ('Metformin', '500mg', 'twice daily'),
            ('Lisinopril', '10mg', 'once daily'),
            ('Atorvastatin', '20mg', 'once daily'),
            ('Omeprazole', '40mg', 'once daily'),
            ('Amlodipine', '5mg', 'once daily')
        ]
        
        statuses = ['active', 'expired', 'completed']
        
        for i in range(min(12, len(patients))):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            medication_name, dosage, frequency = random.choice(medications)
            
            Prescription.objects.create(
                patient=patient,
                prescribed_by=doctor.user,
                medication_name=medication_name,
                dosage=dosage,
                frequency=frequency,
                duration=f"{random.randint(7, 90)} days",
                refills_remaining=random.randint(0, 5),
                status=random.choice(statuses),
                refill_requested=random.choice([True, False])
            )

    def create_lab_tests(self, patients, doctors):
        if not doctors or not patients:
            return
            
        test_names = [
            'Complete Blood Count', 'Lipid Panel', 'Basic Metabolic Panel',
            'Liver Function Test', 'Thyroid Function Test', 'Hemoglobin A1C'
        ]
        
        statuses = ['completed', 'pending', 'normal', 'abnormal']
        
        for i in range(min(15, len(patients))):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            
            test_date = timezone.now() - timedelta(days=random.randint(1, 60))
            
            LabTest.objects.create(
                patient=patient,
                ordered_by=doctor.user,
                test_name=random.choice(test_names),
                test_type=random.choice(['blood', 'urine', 'other']),
                status=random.choice(statuses),
                date_taken=test_date,
                result_value="Within normal limits" if random.choice([True, False]) else "Slightly elevated",
                reference_range="Normal: 10-50",
                is_abnormal=random.choice([True, False])
            )

    def create_vital_signs(self, patients):
        if not patients:
            return
            
        for i in range(min(20, len(patients) * 2)):  # Multiple readings per patient
            patient = random.choice(patients)
            
            measured_date = timezone.now() - timedelta(days=random.randint(1, 30))
            
            VitalSigns.objects.create(
                patient=patient,
                measured_by=patient.user,  # In real scenario, this would be a healthcare worker
                temperature=round(random.uniform(36.1, 38.5), 1),
                blood_pressure_systolic=random.randint(90, 160),
                blood_pressure_diastolic=random.randint(60, 100),
                heart_rate=random.randint(60, 100),
                respiratory_rate=random.randint(12, 20),
                oxygen_saturation=random.randint(95, 100),
                weight=round(random.uniform(50, 120), 1),
                height=random.randint(150, 190),
                measured_at=measured_date,
                date_recorded=measured_date
            )