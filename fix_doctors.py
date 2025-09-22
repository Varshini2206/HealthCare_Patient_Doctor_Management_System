#!/usr/bin/env python
"""
Script to fix Doctor records with duplicate or empty medical license numbers
"""
import os
import django
import sys
import uuid

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_project.settings')
django.setup()

from doctors.models import Doctor

def main():
    print("=== Fixing Doctor Records ===")
    
    # Find doctors with empty or null medical license numbers
    problematic_doctors = Doctor.objects.filter(
        models.Q(medical_license_number__isnull=True) | 
        models.Q(medical_license_number='') |
        models.Q(doctor_id__isnull=True) |
        models.Q(doctor_id='')
    )
    
    print(f"Found {problematic_doctors.count()} doctors with missing identifiers")
    
    for doctor in problematic_doctors:
        print(f"Fixing doctor: {doctor.user.email}")
        
        # Generate unique doctor_id if missing
        if not doctor.doctor_id:
            doctor_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
            while Doctor.objects.filter(doctor_id=doctor_id).exists():
                doctor_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
            doctor.doctor_id = doctor_id
            print(f"  - Assigned doctor_id: {doctor_id}")
        
        # Generate unique medical_license_number if missing
        if not doctor.medical_license_number:
            medical_license = f"ML{str(uuid.uuid4())[:10].upper()}"
            while Doctor.objects.filter(medical_license_number=medical_license).exists():
                medical_license = f"ML{str(uuid.uuid4())[:10].upper()}"
            doctor.medical_license_number = medical_license
            print(f"  - Assigned medical license: {medical_license}")
        
        try:
            doctor.save()
            print(f"  - ✓ Saved successfully")
        except Exception as e:
            print(f"  - ❌ Error saving: {e}")
    
    print("\n=== Checking for Duplicates ===")
    
    # Check for duplicate doctor_ids
    duplicate_doctor_ids = Doctor.objects.values('doctor_id').annotate(
        count=models.Count('doctor_id')
    ).filter(count__gt=1)
    
    if duplicate_doctor_ids:
        print("Found duplicate doctor_ids:")
        for item in duplicate_doctor_ids:
            doctors = Doctor.objects.filter(doctor_id=item['doctor_id'])
            print(f"  Doctor ID '{item['doctor_id']}' used {item['count']} times:")
            for i, doctor in enumerate(doctors):
                if i > 0:  # Keep the first one, change the others
                    new_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
                    while Doctor.objects.filter(doctor_id=new_id).exists():
                        new_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
                    print(f"    - Changing {doctor.user.email} from {doctor.doctor_id} to {new_id}")
                    doctor.doctor_id = new_id
                    doctor.save()
                else:
                    print(f"    - Keeping {doctor.user.email} with {doctor.doctor_id}")
    
    # Check for duplicate medical license numbers
    duplicate_licenses = Doctor.objects.values('medical_license_number').annotate(
        count=models.Count('medical_license_number')
    ).filter(count__gt=1)
    
    if duplicate_licenses:
        print("Found duplicate medical license numbers:")
        for item in duplicate_licenses:
            doctors = Doctor.objects.filter(medical_license_number=item['medical_license_number'])
            print(f"  License '{item['medical_license_number']}' used {item['count']} times:")
            for i, doctor in enumerate(doctors):
                if i > 0:  # Keep the first one, change the others
                    new_license = f"ML{str(uuid.uuid4())[:10].upper()}"
                    while Doctor.objects.filter(medical_license_number=new_license).exists():
                        new_license = f"ML{str(uuid.uuid4())[:10].upper()}"
                    print(f"    - Changing {doctor.user.email} from {doctor.medical_license_number} to {new_license}")
                    doctor.medical_license_number = new_license
                    doctor.save()
                else:
                    print(f"    - Keeping {doctor.user.email} with {doctor.medical_license_number}")
    
    print("\n=== Final Report ===")
    all_doctors = Doctor.objects.all()
    print(f"Total doctors: {all_doctors.count()}")
    for doctor in all_doctors:
        print(f"  - {doctor.user.email}: ID={doctor.doctor_id}, License={doctor.medical_license_number}")

if __name__ == '__main__':
    from django.db import models
    main()