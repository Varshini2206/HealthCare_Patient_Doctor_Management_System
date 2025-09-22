from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from patients.models import Patient
from doctors.models import Doctor
from .models import Appointment
from datetime import datetime


@login_required
def book_appointment(request):
    """Book appointment view"""
    # Ensure user is a patient
    if request.user.user_type != 'patient':
        messages.error(request, 'Only patients can book appointments.')
        return redirect('healthcare_project:home')
    
    patient = get_object_or_404(Patient, user=request.user)
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        appointment_type = request.POST.get('appointment_type', 'consultation')
        consultation_method = request.POST.get('consultation_method', 'in-person')
        
        # Debug: Print form data
        print(f"DEBUG: Form data received:")
        print(f"  doctor_id: {doctor_id}")
        print(f"  appointment_date: {appointment_date}")
        print(f"  appointment_time: {appointment_time}")
        print(f"  reason: {reason}")
        print(f"  appointment_type: {appointment_type}")
        print(f"  consultation_method: {consultation_method}")
        
        # Validate required fields
        if not doctor_id:
            messages.error(request, 'Please select a doctor.')
        elif not appointment_date:
            messages.error(request, 'Please select an appointment date.')
        elif not appointment_time:
            messages.error(request, 'Please select an appointment time.')
        elif not reason:
            messages.error(request, 'Please provide a reason for the visit.')
        else:
            try:
                doctor = Doctor.objects.get(id=doctor_id)
                
                appointment = Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    chief_complaint=reason,  # Map 'reason' to 'chief_complaint'
                    appointment_type=appointment_type,
                    notes=f"Consultation method: {consultation_method}",  # Store consultation method in notes
                    status='scheduled',
                    created_by=request.user  # Add the required created_by field
                )
                
                messages.success(request, 'Appointment request submitted successfully. You will receive confirmation shortly.')
                return redirect('patients:appointments')
                
            except Doctor.DoesNotExist:
                messages.error(request, 'Selected doctor not found.')
            except Exception as e:
                messages.error(request, f'Error booking appointment: {str(e)}')
                print(f"DEBUG: Error creating appointment: {str(e)}")
    
    # Get available doctors
    doctors = Doctor.objects.all().select_related('user')
    today = datetime.now().strftime('%Y-%m-%d')
    
    context = {
        'patient': patient,
        'doctors': doctors,
        'today': today,
    }
    return render(request, 'appointments/book.html', context)


@login_required
def confirm_appointment(request, appointment_id):
    """Confirm appointment view"""
    return render(request, 'appointments/confirm.html')


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel appointment view"""
    # Get the appointment and ensure the user owns it
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has permission to cancel this appointment
    if request.user.user_type == 'patient':
        if appointment.patient.user != request.user:
            messages.error(request, 'You can only cancel your own appointments.')
            return redirect('patients:appointments')
    elif request.user.user_type == 'doctor':
        if appointment.doctor.user != request.user:
            messages.error(request, 'You can only cancel your own appointments.')
            return redirect('doctors:appointments')
    else:
        messages.error(request, 'You do not have permission to cancel appointments.')
        return redirect('healthcare_project:home')
    
    # Check if appointment can be cancelled
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, f'Cannot cancel an appointment that is already {appointment.status}.')
        return redirect('patients:appointments' if request.user.user_type == 'patient' else 'doctors:appointments')
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason')
        
        if cancellation_reason:
            appointment.status = 'cancelled'
            appointment.cancellation_reason = cancellation_reason
            appointment.cancelled_by = request.user
            appointment.cancelled_at = timezone.now()
            appointment.save()
            
            messages.success(request, 'Appointment has been successfully cancelled.')
            return redirect('patients:appointments' if request.user.user_type == 'patient' else 'doctors:appointments')
        else:
            messages.error(request, 'Please provide a reason for cancellation.')
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/cancel.html', context)


@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule appointment view"""
    # Get the appointment and ensure the user owns it
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has permission to reschedule this appointment
    if request.user.user_type == 'patient':
        if appointment.patient.user != request.user:
            messages.error(request, 'You can only reschedule your own appointments.')
            return redirect('patients:appointments')
    elif request.user.user_type == 'doctor':
        if appointment.doctor.user != request.user:
            messages.error(request, 'You can only reschedule your own appointments.')
            return redirect('doctors:appointments')
    else:
        messages.error(request, 'You do not have permission to reschedule appointments.')
        return redirect('healthcare_project:home')
    
    # Check if appointment can be rescheduled
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, f'Cannot reschedule an appointment that is already {appointment.status}.')
        return redirect('patients:appointments' if request.user.user_type == 'patient' else 'doctors:appointments')
    
    if request.method == 'POST':
        new_date = request.POST.get('new_appointment_date')
        new_time = request.POST.get('new_appointment_time')
        reschedule_reason = request.POST.get('reschedule_reason', '')
        
        if new_date and new_time:
            # Check if the new date/time is different from current
            if str(appointment.appointment_date) == new_date and str(appointment.appointment_time) == new_time:
                messages.error(request, 'Please select a different date or time for rescheduling.')
            else:
                # Check for conflicts (same doctor, date, time)
                conflict = Appointment.objects.filter(
                    doctor=appointment.doctor,
                    appointment_date=new_date,
                    appointment_time=new_time,
                    status__in=['scheduled', 'confirmed']
                ).exclude(id=appointment.id).exists()
                
                if conflict:
                    messages.error(request, 'This time slot is already booked. Please choose a different time.')
                else:
                    appointment.appointment_date = new_date
                    appointment.appointment_time = new_time
                    appointment.status = 'rescheduled'
                    if reschedule_reason:
                        appointment.notes += f"\n\nRescheduled: {reschedule_reason}"
                    appointment.save()
                    
                    messages.success(request, 'Appointment has been successfully rescheduled.')
                    return redirect('patients:appointments' if request.user.user_type == 'patient' else 'doctors:appointments')
        else:
            messages.error(request, 'Please select both date and time for the new appointment.')
    
    today = datetime.now().strftime('%Y-%m-%d')
    context = {
        'appointment': appointment,
        'today': today,
    }
    return render(request, 'appointments/reschedule.html', context)


@login_required
def appointment_history(request):
    """Appointment history view"""
    return render(request, 'appointments/history.html')
