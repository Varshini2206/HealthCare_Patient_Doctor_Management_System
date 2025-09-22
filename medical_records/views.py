from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
from .models import MedicalRecord, Prescription, LabResult, VitalSign
from patients.models import Patient
from accounts.models import CustomUser


@login_required
def patient_records(request, patient_id):
    """Patient medical records view"""
    patient = get_object_or_404(Patient, id=patient_id)
    records = MedicalRecord.objects.filter(patient=patient).order_by('-date_created')
    
    # Pagination
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'patient': patient,
        'records': page_obj,
        'total_records': records.count(),
    }
    return render(request, 'medical_records/patient_records.html', context)


@login_required
def prescriptions(request):
    """Prescriptions view"""
    if request.user.user_type == 'patient':
        prescriptions = Prescription.objects.filter(patient__user=request.user).order_by('-date_prescribed')
    else:
        # For doctors, show all prescriptions they've prescribed
        prescriptions = Prescription.objects.filter(prescribed_by=request.user).order_by('-date_prescribed')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        prescriptions = prescriptions.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        prescriptions = prescriptions.filter(
            Q(medication_name__icontains=search_query) |
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(prescriptions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get stats
    active_count = prescriptions.filter(status='active').count()
    expired_count = prescriptions.filter(status='expired').count()
    pending_refills = prescriptions.filter(refill_requested=True).count()
    
    context = {
        'prescriptions': page_obj,
        'active_count': active_count,
        'expired_count': expired_count,
        'pending_refills': pending_refills,
        'total_count': prescriptions.count(),
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'medical_records/prescriptions.html', context)


@login_required
def lab_results(request):
    """Lab results view"""
    if request.user.user_type == 'patient':
        results = LabResult.objects.filter(patient__user=request.user).order_by('-date_taken')
    else:
        # For doctors, show results for their patients
        results = LabResult.objects.filter(ordered_by=request.user).order_by('-date_taken')
    
    # Filter by test type
    test_type = request.GET.get('test_type')
    if test_type:
        results = results.filter(test_type=test_type)
    
    # Filter by date range
    date_range = request.GET.get('date_range')
    if date_range == 'week':
        results = results.filter(date_taken__gte=datetime.now() - timedelta(days=7))
    elif date_range == 'month':
        results = results.filter(date_taken__gte=datetime.now() - timedelta(days=30))
    elif date_range == 'year':
        results = results.filter(date_taken__gte=datetime.now() - timedelta(days=365))
    
    # Pagination
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get recent results for dashboard
    recent_results = results[:5]
    
    # Get stats
    total_tests = results.count()
    abnormal_results = results.filter(status='abnormal').count()
    pending_results = results.filter(status='pending').count()
    
    context = {
        'results': page_obj,
        'recent_results': recent_results,
        'total_tests': total_tests,
        'abnormal_results': abnormal_results,
        'pending_results': pending_results,
        'test_type': test_type,
        'date_range': date_range,
    }
    return render(request, 'medical_records/lab_results.html', context)


@login_required
def vital_signs(request):
    """Vital signs view"""
    if request.user.user_type == 'patient':
        vital_signs = VitalSign.objects.filter(patient__user=request.user).order_by('-date_recorded')
    else:
        # For doctors, show vital signs for their patients
        vital_signs = VitalSign.objects.filter(recorded_by=request.user).order_by('-date_recorded')
    
    # Get recent vital signs for charts
    recent_vitals = vital_signs[:30]  # Last 30 readings for charts
    
    context = {
        'vital_signs': vital_signs[:10],  # Latest 10 for table
        'recent_vitals': recent_vitals,
        'total_readings': vital_signs.count(),
    }
    return render(request, 'medical_records/vital_signs.html', context)


@login_required
def allergies(request):
    """Allergies view"""
    if request.user.user_type == 'patient':
        patient = get_object_or_404(Patient, user=request.user)
    else:
        patient_id = request.GET.get('patient_id')
        if patient_id:
            patient = get_object_or_404(Patient, id=patient_id)
        else:
            patient = None
    
    allergies = []
    if patient:
        # Get patient allergies (this would be from a related model)
        # For now, we'll use sample data
        pass
    
    context = {
        'patient': patient,
        'allergies': allergies,
    }
    return render(request, 'medical_records/allergies.html', context)


@login_required
def medical_history(request):
    """Complete medical history view for patients"""
    if request.user.user_type != 'patient':
        messages.error(request, 'Access denied.')
        return redirect('healthcare_project:home')
    
    patient = get_object_or_404(Patient, user=request.user)
    
    # Get all medical data
    records = MedicalRecord.objects.filter(patient=patient).order_by('-date_created')[:10]
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date_prescribed')[:5]
    lab_results = LabResult.objects.filter(patient=patient).order_by('-date_taken')[:5]
    vital_signs = VitalSign.objects.filter(patient=patient).order_by('-date_recorded')[:5]
    
    # Calculate health metrics
    active_prescriptions = prescriptions.filter(status='active').count()
    recent_tests = lab_results.filter(date_taken__gte=datetime.now() - timedelta(days=30)).count()
    total_appointments = patient.appointment_set.count()
    
    context = {
        'patient': patient,
        'records': records,
        'prescriptions': prescriptions,
        'lab_results': lab_results,
        'vital_signs': vital_signs,
        'active_prescriptions': active_prescriptions,
        'recent_tests': recent_tests,
        'total_appointments': total_appointments,
        'total_records': records.count(),
    }
    return render(request, 'patients/medical_records.html', context)
