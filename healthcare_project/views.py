from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse


def home(request):
    """Home page view"""
    return render(request, 'home.html')


def about(request):
    """About page view"""
    return render(request, 'about.html')


def privacy_policy(request):
    """Privacy Policy page view"""
    return render(request, 'privacy_policy.html')


def terms_of_service(request):
    """Terms of Service page view"""
    return render(request, 'terms_of_service.html')


# Service redirect views with authentication checking
def service_appointments(request):
    """Redirect to appointments service - requires authentication"""
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to access appointment booking services.")
        return redirect(f"{reverse('accounts:login')}?next={request.path}")
    
    # If user is authenticated, redirect based on user type
    if request.user.user_type == 'patient':
        return redirect('patients:appointments')
    elif request.user.user_type == 'doctor':
        return redirect('doctors:appointments')
    else:
        return redirect('appointments:book')


def service_medical_records(request):
    """Redirect to medical records service - requires authentication"""
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to access your medical records.")
        return redirect(f"{reverse('accounts:login')}?next={request.path}")
    
    # If user is authenticated, redirect based on user type
    if request.user.user_type == 'patient':
        return redirect('patients:medical_records')
    elif request.user.user_type == 'doctor':
        messages.info(request, "Doctors can access patient medical records from their dashboard.")
        return redirect('doctors:dashboard')
    else:
        return redirect('patients:medical_records')


def service_prescriptions(request):
    """Redirect to prescriptions service - requires authentication"""
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to access prescription services.")
        return redirect(f"{reverse('accounts:login')}?next={request.path}")
    
    # If user is authenticated, redirect based on user type
    if request.user.user_type == 'patient':
        return redirect('patients:medical_history')  # Prescriptions are part of medical history
    elif request.user.user_type == 'doctor':
        messages.info(request, "Prescription management available in your appointments section.")
        return redirect('doctors:appointments')
    else:
        return redirect('patients:medical_history')


def service_telemedicine(request):
    """Redirect to telemedicine service - requires authentication"""
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to access telemedicine services.")
        return redirect(f"{reverse('accounts:login')}?next={request.path}")
    
    # For now, redirect to appointment booking as telemedicine is handled there
    messages.info(request, "Telemedicine consultations can be booked through our appointment system.")
    if request.user.user_type == 'patient':
        return redirect('appointments:book')
    elif request.user.user_type == 'doctor':
        return redirect('doctors:appointments')
    else:
        return redirect('appointments:book')