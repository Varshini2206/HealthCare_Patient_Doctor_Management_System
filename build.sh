#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify pip.conf to use global install
export PIP_USER=0

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install additional production dependencies
echo "📦 Installing production dependencies..."
pip install gunicorn whitenoise dj-database-url psycopg2-binary

echo "🗃️ Collecting static files..."
python manage.py collectstatic --no-input

echo "🔄 Running database migrations..."
python manage.py migrate

echo "👥 Creating demo users if they don't exist..."
python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

# Create superuser if doesn't exist
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@vbhealthcare.com', 'admin123')
    print("✅ Created admin user")

# Create demo patient if doesn't exist
if not User.objects.filter(username='patient_demo').exists():
    patient_user = User.objects.create_user(
        username='patient_demo',
        email='patient@demo.com',
        password='demo123',
        first_name='John',
        last_name='Patient'
    )
    UserProfile.objects.create(
        user=patient_user,
        user_type='patient',
        phone='+1234567890'
    )
    print("✅ Created demo patient")

# Create demo doctor if doesn't exist  
if not User.objects.filter(username='doctor_demo').exists():
    doctor_user = User.objects.create_user(
        username='doctor_demo',
        email='doctor@demo.com', 
        password='demo123',
        first_name='Dr. Sarah',
        last_name='Smith'
    )
    UserProfile.objects.create(
        user=doctor_user,
        user_type='doctor',
        phone='+1234567891'
    )
    print("✅ Created demo doctor")

EOF

echo "✅ Build completed successfully!"