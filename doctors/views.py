from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
from .models import Doctor
from patients.models import Patient
from appointments.models import Appointment
# Temporarily disabled medical records imports until migrations are fixed
# from medical_records.models import MedicalRecord


@login_required
def doctor_dashboard(request):
    """Doctor dashboard view"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied. You must be logged in as a doctor to access this page.')
        return redirect('healthcare_project:home')
    
    # Get or create doctor record if it doesn't exist
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        # Generate unique identifiers
        doctor_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
        medical_license = f"ML{str(uuid.uuid4())[:10].upper()}"
        
        # Ensure uniqueness
        while Doctor.objects.filter(doctor_id=doctor_id).exists():
            doctor_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
        while Doctor.objects.filter(medical_license_number=medical_license).exists():
            medical_license = f"ML{str(uuid.uuid4())[:10].upper()}"
        
        # Create a doctor record if it doesn't exist
        doctor = Doctor.objects.create(
            user=request.user,
            doctor_id=doctor_id,
            medical_license_number=medical_license,
            years_of_experience=0,
            is_verified=False
        )
        messages.info(request, 'Doctor profile created successfully.')
    
    today = timezone.now().date()
    
    # Get dashboard statistics
    # Get patients through appointments (since patients don't have direct doctor field)
    total_patients = Patient.objects.filter(appointments__doctor=doctor).distinct().count()
    today_appointments = Appointment.objects.filter(
        doctor=doctor, 
        appointment_date=today
    ).count()
    pending_appointments = Appointment.objects.filter(
        doctor=doctor, 
        status='pending'
    ).count()
    completed_appointments = Appointment.objects.filter(
        doctor=doctor, 
        status='completed'
    ).count()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=today,
        status__in=['confirmed', 'pending', 'scheduled']
    ).order_by('appointment_date', 'appointment_time')[:5]
    
    # Get recent patients (through appointments)
    recent_patients = Patient.objects.filter(appointments__doctor=doctor).distinct().order_by('-created_at')[:5]
    
    context = {
        'doctor': doctor,
        'total_patients': total_patients,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_patients': recent_patients,
    }
    return render(request, 'doctors/dashboard.html', context)


@login_required
def doctor_profile(request):
    """Doctor profile view"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('healthcare_project:home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    
    if request.method == 'POST':
        # Handle profile update
        doctor.specialization = request.POST.get('specialization', doctor.specialization)
        doctor.qualifications = request.POST.get('qualifications', doctor.qualifications)
        doctor.experience_years = request.POST.get('experience_years', doctor.experience_years)
        doctor.consultation_fee = request.POST.get('consultation_fee', doctor.consultation_fee)
        doctor.save()
        
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.phone_number = request.POST.get('phone_number', request.user.phone_number)
        request.user.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('doctors:profile')
    
    context = {
        'doctor': doctor,
    }
    return render(request, 'doctors/profile.html', context)


@login_required
def doctor_appointments(request):
    """Doctor appointments view"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('healthcare_project:home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    today = timezone.now().date()
    
    # Get appointments
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date', '-appointment_time')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    # Filter by date
    date_filter = request.GET.get('date_range')
    if date_filter == 'today':
        appointments = appointments.filter(appointment_date=today)
    elif date_filter == 'week':
        appointments = appointments.filter(appointment_date__range=[today, today + timedelta(days=7)])
    elif date_filter == 'month':
        appointments = appointments.filter(appointment_date__range=[today, today + timedelta(days=30)])
    
    # Get today's schedule
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).order_by('appointment_time')
    
    # Get this week's appointments
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__range=[week_start, week_end]
    ).order_by('appointment_date', 'appointment_time')
    
    # Pagination
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get stats
    total_appointments = appointments.count()
    confirmed_count = appointments.filter(status='confirmed').count()
    pending_count = appointments.filter(status='pending').count()
    completed_count = appointments.filter(status='completed').count()
    
    context = {
        'doctor': doctor,
        'appointments': page_obj,
        'today_appointments': today_appointments,
        'week_appointments': week_appointments,
        'total_appointments': total_appointments,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    return render(request, 'doctors/appointments.html', context)


@login_required
def doctor_patients(request):
    """Doctor patients view"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('healthcare_project:home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    
    # Get all patients (through appointments)
    patients = Patient.objects.filter(appointments__doctor=doctor).distinct().select_related('user')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        patients = patients.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(medical_record_number__icontains=search_query)
        )
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        # This would require adding a priority field to the Patient model
        pass
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get stats
    total_patients = patients.count()
    
    # Get patients with recent appointments (last 30 days)
    recent_patients = patients.filter(
        appointments__appointment_date__gte=timezone.now().date() - timedelta(days=30)
    ).distinct().count()
    
    # Get patients needing follow-up (this would need additional logic)
    followup_patients = 8  # Sample number
    
    # Get critical patients (this would need additional logic based on medical conditions)
    critical_patients = 5  # Sample number
    
    context = {
        'doctor': doctor,
        'patients': page_obj,
        'total_patients': total_patients,
        'recent_patients': recent_patients,
        'followup_patients': followup_patients,
        'critical_patients': critical_patients,
        'search_query': search_query,
        'priority_filter': priority_filter,
    }
    return render(request, 'doctors/patients.html', context)


@login_required
def doctor_schedule(request):
    """Doctor schedule view"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('healthcare_project:home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    
    # Get schedule for the current week
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    weekly_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__range=[week_start, week_end]
    ).order_by('appointment_date', 'appointment_time')
    
    context = {
        'doctor': doctor,
        'weekly_appointments': weekly_appointments,
        'week_start': week_start,
        'week_end': week_end,
    }
    return render(request, 'doctors/schedule.html', context)


@login_required
def confirm_appointment(request, appointment_id):
    """Confirm/Accept appointment request"""
    if request.user.user_type != 'doctor':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == 'POST':
        try:
            appointment.status = 'confirmed'
            appointment.confirmed_at = timezone.now()
            appointment.save()
            
            messages.success(request, f'Appointment with {appointment.patient.user.get_full_name()} confirmed successfully.')
            
            return JsonResponse({
                'success': True,
                'message': 'Appointment confirmed successfully',
                'appointment_id': appointment_id,
                'new_status': 'confirmed'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def reject_appointment(request, appointment_id):
    """Reject appointment request"""
    if request.user.user_type != 'doctor':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == 'POST':
        try:
            reason = request.POST.get('reason', '')
            appointment.status = 'cancelled'
            appointment.cancelled_at = timezone.now()
            appointment.cancellation_reason = reason
            appointment.save()
            
            messages.success(request, f'Appointment with {appointment.patient.user.get_full_name()} rejected.')
            
            return JsonResponse({
                'success': True,
                'message': 'Appointment rejected successfully',
                'appointment_id': appointment_id,
                'new_status': 'cancelled'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def complete_appointment(request, appointment_id):
    """Mark appointment as completed and add medical notes"""
    if request.user.user_type != 'doctor':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == 'POST':
        try:
            # Update appointment status
            appointment.status = 'completed'
            appointment.doctor_notes = request.POST.get('notes', appointment.doctor_notes)
            appointment.follow_up_required = request.POST.get('follow_up_required') == 'on'
            
            if request.POST.get('follow_up_date'):
                from datetime import datetime
                appointment.follow_up_date = datetime.strptime(request.POST.get('follow_up_date'), '%Y-%m-%d').date()
            
            appointment.follow_up_instructions = request.POST.get('follow_up_instructions', appointment.follow_up_instructions)
            appointment.save()
            
            messages.success(request, f'Appointment with {appointment.patient.user.get_full_name()} completed successfully.')
            
            return JsonResponse({
                'success': True,
                'message': 'Appointment completed successfully',
                'appointment_id': appointment_id,
                'new_status': 'completed'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule appointment"""
    if request.user.user_type != 'doctor':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == 'POST':
        try:
            new_date = request.POST.get('new_date')
            new_time = request.POST.get('new_time')
            reason = request.POST.get('reason', '')
            
            if not new_date or not new_time:
                return JsonResponse({'error': 'New date and time are required'}, status=400)
            
            # Parse the new date and time
            from datetime import datetime
            new_appointment_date = datetime.strptime(new_date, '%Y-%m-%d').date()
            new_appointment_time = datetime.strptime(new_time, '%H:%M').time()
            
            # Update appointment
            appointment.appointment_date = new_appointment_date
            appointment.appointment_time = new_appointment_time
            appointment.status = 'rescheduled'
            
            # Add reschedule reason to notes
            if reason:
                reschedule_note = f"\n\n[RESCHEDULED] {timezone.now().strftime('%Y-%m-%d %H:%M')}: {reason}"
                appointment.doctor_notes = (appointment.doctor_notes or "") + reschedule_note
            
            appointment.save()
            
            messages.success(request, f'Appointment with {appointment.patient.user.get_full_name()} rescheduled successfully.')
            
            return JsonResponse({
                'success': True,
                'message': 'Appointment rescheduled successfully',
                'appointment_id': appointment_id,
                'new_date': new_date,
                'new_time': new_time,
                'new_status': 'rescheduled'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def patient_details(request, patient_id):
    """View patient details for doctors"""
    if request.user.user_type != 'doctor':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    doctor = get_object_or_404(Doctor, user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Check if doctor has treated this patient
    has_appointment = Appointment.objects.filter(doctor=doctor, patient=patient).exists()
    if not has_appointment:
        return JsonResponse({'error': 'Access denied - No appointment history'}, status=403)
    
    # Get appointment history
    appointments = Appointment.objects.filter(doctor=doctor, patient=patient).order_by('-appointment_date')
    
    # Get user profile for emergency contact info
    user_profile = getattr(patient.user, 'profile', None)
    
    # Get basic patient info - using correct field names from the models
    patient_data = {
        'id': patient.id,
        'name': patient.user.get_full_name() or patient.user.username,
        'email': patient.user.email,
        'phone': patient.user.phone_number or '',
        'date_of_birth': patient.user.date_of_birth.strftime('%Y-%m-%d') if patient.user.date_of_birth else '',
        'gender': dict(patient.GENDER_CHOICES).get(patient.gender, patient.gender) if patient.gender else '',
        'blood_type': patient.blood_group or '',
        'emergency_contact': user_profile.emergency_contact_name if user_profile else '',
        'emergency_phone': user_profile.emergency_contact_phone if user_profile else '',
        'medical_history': patient.family_medical_history or '',
        'allergies': patient.known_allergies or '',
        'current_medications': patient.current_medications or '',
        'appointments': [
            {
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status,
                'chief_complaint': apt.chief_complaint or '',
                'diagnosis': apt.doctor_notes or '',  # Using doctor_notes as diagnosis
                'prescription': '',  # Not available in current model
                'notes': apt.notes or ''
            } for apt in appointments
        ]
    }
    
    return JsonResponse({'success': True, 'patient': patient_data})


@login_required
def patient_profile(request, patient_id):
    """Comprehensive patient profile view for doctors"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('healthcare_project:home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Check if doctor has treated this patient
    has_appointment = Appointment.objects.filter(doctor=doctor, patient=patient).exists()
    if not has_appointment:
        messages.error(request, 'Access denied - No appointment history with this patient.')
        return redirect('doctors:dashboard')
    
    # Get comprehensive patient data
    patient_appointments = Appointment.objects.filter(
        doctor=doctor, 
        patient=patient
    ).order_by('-appointment_date', '-appointment_time')
    
    # Get patient documents
    patient_documents = []
    try:
        from django.apps import apps
        if apps.is_installed('patients'):
            from patients.models import PatientDocument
            patient_documents = PatientDocument.objects.filter(
                patient=patient
            ).order_by('-upload_date')
    except (ImportError, LookupError):
        pass
    
    # Get medical records if available
    medical_records = []
    try:
        from django.apps import apps
        if apps.is_installed('medical_records'):
            from medical_records.models import MedicalRecord
            medical_records = MedicalRecord.objects.filter(
                patient=patient
            ).order_by('-created_at')
    except (ImportError, LookupError, RuntimeError):
        # medical_records app not available or not properly configured
        pass
    
    # Get user profile for emergency contact
    user_profile = getattr(patient.user, 'profile', None)
    
    # Calculate patient age
    patient_age = None
    if patient.user.date_of_birth:
        from datetime import date
        today = date.today()
        patient_age = today.year - patient.user.date_of_birth.year - (
            (today.month, today.day) < (patient.user.date_of_birth.month, patient.user.date_of_birth.day)
        )
    
    # Get appointment statistics
    total_appointments = patient_appointments.count()
    completed_appointments = patient_appointments.filter(status='completed').count()
    cancelled_appointments = patient_appointments.filter(status='cancelled').count()
    
    context = {
        'doctor': doctor,
        'patient': patient,
        'patient_age': patient_age,
        'user_profile': user_profile,
        'patient_appointments': patient_appointments,
        'patient_documents': patient_documents,
        'medical_records': medical_records,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
    }
    return render(request, 'doctors/patient_profile.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """View appointment details with comprehensive patient information"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('healthcare_project:home')
    
    # Get or create doctor record if it doesn't exist
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = Doctor.objects.create(
            user=request.user,
            medical_license_number=f'ML{request.user.id:06d}',
            years_of_experience=0,
            is_verified=False
        )
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    patient = appointment.patient
    
    # Get comprehensive patient data
    # Get all appointments for this patient with this doctor
    patient_appointments = Appointment.objects.filter(
        doctor=doctor, 
        patient=patient
    ).order_by('-appointment_date', '-appointment_time')
    
    # Get patient documents if the model exists
    patient_documents = []
    try:
        from patients.models import PatientDocument
        patient_documents = PatientDocument.objects.filter(
            patient=patient
        ).order_by('-upload_date')
    except ImportError:
        pass
    
    # Get user profile for emergency contact
    user_profile = getattr(patient.user, 'profile', None)
    
    # Calculate patient age
    patient_age = None
    today = None
    if patient.user.date_of_birth:
        from datetime import date
        today = date.today()
        patient_age = today.year - patient.user.date_of_birth.year - (
            (today.month, today.day) < (patient.user.date_of_birth.month, patient.user.date_of_birth.day)
        )
    else:
        from datetime import date
        today = date.today()
    
    context = {
        'doctor': doctor,
        'appointment': appointment,
        'patient': patient,
        'patient_age': patient_age,
        'user_profile': user_profile,
        'patient_appointments': patient_appointments,
        'patient_documents': patient_documents,
        'appointment_count': patient_appointments.count(),
        'today': today,
    }
    return render(request, 'doctors/appointment_detail.html', context)
