from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json

from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
# from medical_records.models import MedicalRecord


@login_required
def analytics_dashboard(request):
    """
    Main analytics dashboard view
    """
    # Get basic statistics
    stats = {
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_doctors': Doctor.objects.filter(is_verified=True).count(),
        'total_appointments': Appointment.objects.count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
    }
    
    # Get chart data
    chart_data = get_dashboard_chart_data()
    
    # Get recent activities
    recent_activities = get_recent_activities()
    
    context = {
        'stats': stats,
        'chart_data': chart_data,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'dashboard/analytics.html', context)


def get_dashboard_chart_data(period='month'):
    """
    Generate chart data for the dashboard
    """
    now = timezone.now()
    
    # Determine date range based on period
    if period == 'week':
        start_date = now - timedelta(days=7)
        date_format = '%m-%d'
    elif period == 'quarter':
        start_date = now - timedelta(days=90)
        date_format = '%Y-%m'
    else:  # month
        start_date = now - timedelta(days=30)
        date_format = '%m-%d'
    
    # Appointment trends data
    appointment_data = []
    appointment_labels = []
    
    current_date = start_date
    while current_date <= now:
        date_str = current_date.strftime(date_format)
        count = Appointment.objects.filter(
            created_at__date=current_date.date()
        ).count()
        
        appointment_labels.append(date_str)
        appointment_data.append(count)
        current_date += timedelta(days=1)
    
    # Status distribution data
    status_counts = Appointment.objects.values('status').annotate(count=Count('status'))
    status_labels = [item['status'].title() for item in status_counts]
    status_data = [item['count'] for item in status_counts]
    
    # Specialization data
    specialization_counts = Doctor.objects.values('specialization').annotate(count=Count('specialization'))
    specialization_labels = [item['specialization'] for item in specialization_counts]
    specialization_data = [item['count'] for item in specialization_counts]
    
    return {
        'appointment_labels': json.dumps(appointment_labels),
        'appointment_data': json.dumps(appointment_data),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'specialization_labels': json.dumps(specialization_labels),
        'specialization_data': json.dumps(specialization_data),
    }


def get_recent_activities():
    """
    Get recent system activities
    """
    activities = []
    
    # Recent appointments
    recent_appointments = Appointment.objects.select_related(
        'patient__user', 'doctor__user'
    ).order_by('-created_at')[:5]
    
    for appointment in recent_appointments:
        activities.append({
            'type': 'appointment',
            'description': f"New appointment scheduled with Dr. {appointment.doctor.user.get_full_name()} for {appointment.patient.user.get_full_name()}",
            'timestamp': appointment.created_at,
        })
    
    # Recent patient registrations
    recent_patients = Patient.objects.select_related('user').order_by('-created_at')[:3]
    for patient in recent_patients:
        activities.append({
            'type': 'patient',
            'description': f"New patient registered: {patient.user.get_full_name()}",
            'timestamp': patient.created_at,
        })
    
    # Recent medical records - Temporarily disabled
    # try:
    #     recent_records = MedicalRecord.objects.select_related(
    #         'patient__user', 'doctor__user'
    #     ).order_by('-created_at')[:3]
    #     
    #     for record in recent_records:
    #         activities.append({
    #             'type': 'medical_record',
    #             'description': f"Medical record created for {record.patient.user.get_full_name()}",
    #             'timestamp': record.created_at,
    #         })
    # except:
    #     # Handle case where MedicalRecord table doesn't exist yet
    #     pass
    
    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return activities[:10]


@login_required
def live_stats(request):
    """
    HTMX endpoint for live statistics updates
    """
    stats = {
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_doctors': Doctor.objects.filter(is_verified=True).count(),
        'total_appointments': Appointment.objects.count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
    }
    
    return render(request, 'partials/live_stats.html', {'stats': stats})


@login_required
def chart_data(request):
    """
    HTMX endpoint for dynamic chart data updates
    """
    period = request.GET.get('period', 'month')
    chart_type = request.GET.get('chart_type', 'line')
    
    chart_data = get_dashboard_chart_data(period)
    
    return JsonResponse({
        'chart_data': chart_data,
        'chart_type': chart_type
    })


@login_required
def recent_activity(request):
    """
    HTMX endpoint for recent activity updates
    """
    recent_activities = get_recent_activities()
    
    return render(request, 'partials/activity_feed.html', {
        'recent_activities': recent_activities
    })


@login_required
def patient_analytics(request):
    """
    Patient-specific analytics view
    """
    if request.user.user_type != 'patient':
        return render(request, 'error/403.html')
    
    try:
        patient = Patient.objects.get(user=request.user)
        
        # Patient-specific statistics
        stats = {
            'total_appointments': Appointment.objects.filter(patient=patient).count(),
            'upcoming_appointments': Appointment.objects.filter(
                patient=patient,
                appointment_date__gte=timezone.now().date(),
                status__in=['confirmed', 'pending']
            ).count(),
            'completed_appointments': Appointment.objects.filter(
                patient=patient, status='completed'
            ).count(),
        }
        
        # Upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_date__gte=timezone.now().date(),
            status__in=['confirmed', 'pending']
        ).select_related('doctor__user').order_by('appointment_date', 'appointment_time')[:5]
        
        context = {
            'stats': stats,
            'upcoming_appointments': upcoming_appointments,
            'patient': patient,
        }
        
        return render(request, 'dashboard/patient_analytics.html', context)
        
    except Patient.DoesNotExist:
        return render(request, 'error/404.html')


@login_required
def doctor_analytics(request):
    """
    Doctor-specific analytics view
    """
    if request.user.user_type != 'doctor':
        return render(request, 'error/403.html')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
        
        # Doctor-specific statistics
        stats = {
            'total_appointments': Appointment.objects.filter(doctor=doctor).count(),
            'today_appointments': Appointment.objects.filter(
                doctor=doctor,
                appointment_date=timezone.now().date()
            ).count(),
            'total_patients': Appointment.objects.filter(
                doctor=doctor
            ).values('patient').distinct().count(),
            'pending_appointments': Appointment.objects.filter(
                doctor=doctor, status='pending'
            ).count(),
        }
        
        # Today's appointments
        today_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=timezone.now().date()
        ).select_related('patient__user').order_by('appointment_time')
        
        context = {
            'stats': stats,
            'today_appointments': today_appointments,
            'doctor': doctor,
        }
        
        return render(request, 'dashboard/doctor_analytics.html', context)
        
    except Doctor.DoesNotExist:
        return render(request, 'error/404.html')