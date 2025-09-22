from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='dashboard'),
    path('profile/', views.doctor_profile, name='profile'),
    path('appointments/', views.doctor_appointments, name='appointments'),
    path('patients/', views.doctor_patients, name='patients'),
    path('schedule/', views.doctor_schedule, name='schedule'),
    
    # Appointment management
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('appointments/<int:appointment_id>/reject/', views.reject_appointment, name='reject_appointment'),
    path('appointments/<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('appointments/<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    
    # Patient details
    path('patients/<int:patient_id>/', views.patient_details, name='patient_details'),
    path('patients/<int:patient_id>/profile/', views.patient_profile, name='patient_profile'),
]