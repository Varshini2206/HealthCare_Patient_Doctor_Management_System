import os
import sys
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_user(
            username='admin',
            email='admin@healthcenter.com',
            password='admin123',
            first_name='System',
            last_name='Administrator',
            user_type='admin',
            is_staff=True,
            is_superuser=True
        )
        print("✓ Admin user created successfully")
        print("  Username: admin")
        print("  Password: admin123")
    else:
        print("✓ Admin user already exists")
        
    # Create sample doctor
    if not User.objects.filter(username='dr_sarah').exists():
        doctor_user = User.objects.create_user(
            username='dr_sarah',
            email='sarah.johnson@healthcenter.com',
            password='healthpass123',
            first_name='Sarah',
            last_name='Johnson',
            user_type='doctor',
            phone_number='+15551234567'
        )
        print("✓ Sample doctor created")
        print("  Username: dr_sarah")
        print("  Password: healthpass123")
    else:
        print("✓ Sample doctor already exists")
        
    # Create sample patient
    if not User.objects.filter(username='patient_john').exists():
        patient_user = User.objects.create_user(
            username='patient_john',
            email='john.smith@email.com',
            password='patientpass123',
            first_name='John',
            last_name='Smith',
            user_type='patient',
            phone_number='+15559876543'
        )
        print("✓ Sample patient created")
        print("  Username: patient_john")
        print("  Password: patientpass123")
    else:
        print("✓ Sample patient already exists")
        
except Exception as e:
    print(f"Error creating users: {e}")